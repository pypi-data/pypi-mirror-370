import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup    
from easy_utils_dev.simple_sqlite import initDB
from easy_utils_dev.utils import getRandomKey , getTimestamp , lget , mkdirs
import json , os , glob
from easy_utils_dev.FastQueue import FastQueue
from easy_utils_dev.debugger import DEBUGGER 
import zipfile
import tempfile


__LIBPATH__ = os.path.dirname(os.path.abspath(__file__))
MAPPER = {
    'PSS32' : {
        "PHY" :[2,20,3,21,4,22,5,23,6,24,7,25,8,26,9,27,10,28,11,29,12,30,13,31,14,32,15,33,16,34,17,35]
    } ,
    'PSS16II' : {
        "PHY" :[3,13,4,14,5,15,6,16,7,17,8,18,9,19,10,20]
    } ,
    'PSS16' : {
        "PHY" :[3,13,4,14,5,15,6,16,7,17,8,18,9,19,10,20]
    } ,
    'PSS8' : {
        "PHY" :[2,8,3,9,4,10,5,11]
    } ,
}
ns = {"ept": "http://upm.lucent.com/EPTdesign"}

class EPTManager : 
    def __init__(self , 
                design_path,
                include_parent_attrs=True , 
                include_grantparent_attrs=False , 
                ept_db_path=f"ept_{getTimestamp()}.db" ,
                debug_name='EPTManager',
                debug_home_path=None
        ) -> None:
        self.root = None
        self.logger = DEBUGGER(name=debug_name, homePath=debug_home_path)
        self.design_path = design_path
        self.ept_db_path = ept_db_path
        self.include_parent_attrs = include_parent_attrs
        self.include_grantparent_attrs = include_grantparent_attrs
        self.sites = []
        self.queue = FastQueue(request_max_count=4)
        self.nes = []
        self.tmp_design_path = None
        
    
    def convert_slotid_to_physical_slot(self , shType , slotid ) :
        slotid = int(slotid) - 1
        return MAPPER[shType]['PHY'][slotid]
        
    def fix_xml_file(self , xml_content ) :
        xml_content = xml_content.splitlines() 
        for i , line in enumerate(xml_content) :
            if '<EPTdesign' in line :
                line = line.split(' ')[0]
                line = f"{line}>"
                xml_content[i] = line
                break
        return ''.join(xml_content) 
    
    def Database(self) :
        db = initDB()
        db.config_database_path(self.ept_db_path)
        return db

    def create_ept_columns(self , drop_cols=[]) :
        self.logger.info("Creating EPT Database Tables ...")
        db = self.Database()
        drop_cols = [str(col).upper() for col in drop_cols]
        tags = [str(tag.name) for tag in self.root.find_all() ]
        tags = list(set(tags))
        for tagName in tags :
            tags = self.root.find_all(tagName)
            tableColumns = [
                {
                    'column' : 'parentId' ,
                    'params' : 'TEXT'
                },
                {
                    'column' : 'parentTag' ,
                    'params' : 'TEXT'
                },
                {
                    'column' : 'parentAttrs' ,
                    'params' : 'TEXT'
                },
                {
                    'column' : 'grandparentId' ,
                    'params' : 'TEXT'
                },
                {
                    'column' : 'grandparentTag' ,
                    'params' : 'TEXT'
                },
                {
                    'column' : 'grandparentAttrs' ,
                    'params' : 'TEXT'
                },
            ]
            added = []
            for tag in tags :
                attrs = tag.attrs
                for attr in list(attrs.keys()) :
                    _input = {
                        'column' : str(attr) ,
                        'params' : 'TEXT'
                    }
                    if not str(attr).upper() in added and not str(attr).upper() in drop_cols :
                        if '-' in str(attr) :
                            continue
                        self.logger.debug(f'[{tagName}] : Adding Column : {_input}')
                        tableColumns.append(_input)
                        added.append(str(attr).upper())
            if len(tableColumns) > 0 :
                db.createTable( tableName=tagName , data=tableColumns , autoId=False )

    def create_ept_rows(self) :
        self.logger.info("Creating EPT Rows ...")
        tags = [str(tag.name) for tag in self.root.find_all() ]
        tags = list(set(tags))
        db = initDB()
        db.config_database_path(self.ept_db_path)
        for tableName in tags :
            tags = self.root.find_all(tableName)
            rows = []
            query = f"PRAGMA table_info({tableName})"
            columns = db.execute_dict(query)
            for tag in tags :
                template = {}
                for column in columns :
                    template[column['name']] = None
                attrs = tag.attrs
                if len(list(attrs.keys())) > 0 :
                    for key , _ in template.items() :
                        template[key] = attrs.get(key , None)
                    template['parentId'] = tag.parent.attrs.get('id')
                    template['parentTag'] = tag.parent.name
                    template['grandparentId'] = tag.parent.parent.attrs.get('id')
                    template['grandparentTag'] = tag.parent.parent.name
                    if self.include_parent_attrs :
                        template['parentAttrs'] = json.dumps(tag.parent.attrs)
                    if self.include_grantparent_attrs :
                        template['grandparentAttrs'] = json.dumps(tag.parent.parent.attrs)
                    rows.append(template)
                    # print(f"[{tableName}] : Adding Row ")
            if len(rows) > 0 :
                db.insert_to_table_bulk(tableName=tableName , values=rows)
                
    def parse(self) :
        if self.design_path.endswith('.ept') :
            self.extract_ept(self.design_path)

        with open(self.design_path , 'r') as file :
            xml_content = file.read()
        xml_content  = self.fix_xml_file(xml_content)
        self.root = BeautifulSoup( xml_content, 'xml')
        return self.root
    
    def extract_ept(self , ept_path):
        extract_to = tempfile.gettempdir() + f"/ept_extraction"
        self.logger.debug(f"Extracting .EPT content to '{extract_to}'")
        mkdirs(extract_to)
        with zipfile.ZipFile(ept_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        xml_dir = glob.glob(f"{extract_to}/*.xml")[0]
        self.design_path = xml_dir
        self.tmp_design_path = xml_dir
        self.logger.debug(f"EPT.XML location '{xml_dir}'")
        return xml_dir
        
    def _create_v_dirs(self) :
        db = self.Database()
        dirs = self.get_all_dirs()

        db.createTable(
            'c_dirs' ,
            data=[
                                {
                    'column' : 'SOURCESITE' , 
                    'params' : 'TEXT'
                },
                {
                    'column' : 'SOURCEPACKID' , 
                    'params' : 'TEXT'
                },
                {
                    'column' : 'SPANID' , 
                    'params' : 'TEXT'
                },
                {
                    'column' : 'SOURCEAPN' , 
                    'params' : 'TEXT'
                },
                {
                    'column' : 'SOURCEPACKIDREF' , 
                    'params' : 'TEXT'
                },
                {
                    'column' : 'DESTINATIONSITE' , 
                    'params' : 'TEXT'
                },
                {
                    'column' : 'SOURCEBOARD' , 
                    'params' : 'TEXT'
                },
                {
                    'column' : 'SOURCEPHYSICALSLOT' , 
                    'params' : 'TEXT'
                },
                {
                    'column' : 'FULLSLOT' , 
                    'params' : 'TEXT'
                },
                {
                    'column' : 'SHELFTYPE' , 
                    'params' : 'TEXT'
                }
            ]
        )
        db.insert_to_table_bulk(tableName='c_dirs' , values=dirs)

    
    def get_site_data_by_id(self , id ) -> dict :
        db = self.Database()
        query = f"select * from site where id='{id}' "
        siteData = lget(db.execute_dict(query) , 0 , {})
        return siteData

    def get_all_amplifiers(self) : 
        db = self.Database()
        query = f"select * from circuitpack where packIDRef IS NOT NULL and type in (select packName from OAtype where packName is NOT NULL or packName != '')"
        packs = db.execute_dict(query)
        return packs
    
    def get_shelf_data_by_id(self , id ) -> dict :
        db = self.Database()
        query = f"select * from shelf where id='{id}' "
        shelfData = lget(db.execute_dict(query) , 0 , {})
        return shelfData
    
    def get_ne_data_by_id(self , id ) -> dict :
        db = self.Database()
        query = f"select * from ne where id='{id}' "
        neData = lget(db.execute_dict(query) , 0 , {})
        return neData
    
    
    def get_table_data_by_id(self , table , id ) :
        db = self.Database()
        query = f"select * from {table} where id='{id}' "
        data = lget(db.execute_dict(query) , 0 , {})
        return data

    def convert_design(self , drop_cols=[] ) :
        start = getTimestamp()
        db = self.Database()
        self.parse()
        self.create_ept_columns(drop_cols=drop_cols)
        self.create_ept_rows()
        db.execute_script(f"{os.path.join(__LIBPATH__ , 'ept_sql' , 'create_dirs.sql')}")
        self._create_v_dirs()
        end = getTimestamp()
        if os.path.exists(self.tmp_design_path) :
            os.remove(self.tmp_design_path)
        self.logger.info(f"Design converted in {round((end - start)/60 , 2)} mins")

    def get_all_dirs(self, filter_source_ne=None) : 
        db = self.Database()
        packs = self.get_all_amplifiers()
        _packs = []
        def __g_p(pack) : 
            parentId = pack['parentId']
            wdmline = pack['wdmline']
            shelf = self.get_shelf_data_by_id(parentId)
            shelfNumber = shelf['number']
            shelfType = shelf['type']
            physicalslot = self.convert_slotid_to_physical_slot(shelfType , pack.get('slotid'))
            grandparentId = shelf['grandparentId']
            ne = self.get_site_data_by_id(grandparentId)
            sourceNE = ne['name']
            if filter_source_ne and filter_source_ne != sourceNE : 
                return
            span = self.get_table_data_by_id('line' , wdmline)
            spanId = span['span']
            query = f"select grandparentId from line where span='{spanId}' "
            spans = db.execute_dict(query)
            for span in spans :
                siteData = self.get_site_data_by_id(span['grandparentId'])
                if siteData.get('name') != sourceNE :
                    DestinationNE = siteData.get('name')
                    break
            fullSlot = f"{shelfNumber}/{physicalslot}"
            _packs.append({
                'SOURCESITE' : sourceNE , 
                'SOURCEPACKID' : pack.get('id') , 
                "SPANID" : spanId , 
                'SOURCEAPN' : pack.get('apn') , 
                'SOURCEPACKIDREF' : pack.get('packidref') , 
                'DESTINATIONSITE' : DestinationNE , 
                'SOURCEBOARD' : pack.get('type') , 
                'SOURCEPHYSICALSLOT' : physicalslot , 
                'FULLSLOT' : fullSlot , 
                'SHELFTYPE' : shelfType ,
            })
            self.logger.debug(f"Source:{sourceNE}/{fullSlot}/{pack.get('type')} -> {spanId} -> {DestinationNE}")
        for pack in packs : 
            self.queue.addToQueue(action=__g_p , actionArgs={'pack' : pack})
        self.queue.runQueue(maxRequests=10)
        return _packs
            

if __name__ == "__main__" :
    # XMLFILEPATH = "IGG_2.2_08122025.xml"
    XMLFILEPATH = "IGG_2.2_08122025.xml"
    ept = EPTManager(
        ept_db_path=f"ept_mcc.db" ,
        design_path=XMLFILEPATH,
        include_parent_attrs=True , 
        include_grantparent_attrs=False
    )
    ## Convert XML to EPT Database
    # ept.parse()
    # ept.create_ept_columns(drop_cols=[])
    # ept.create_ept_rows()
    
    # # Get All Dirs
    # with open(f"ept_{getTimestamp()}.json" , 'w') as file :
    #     file.write(json.dumps(ept.get_all_dirs() , indent=4))


# from easy_utils_dev.simple_sqlite import initDB

# db = initDB()
# db.config_database_path("ept_1755437540.db")
# print(db.execute_script("create_dirs.sql"))