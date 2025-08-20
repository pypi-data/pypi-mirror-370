import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup    
from easy_utils_dev.simple_sqlite import initDB
from easy_utils_dev.utils import getRandomKey , getTimestamp , lget , mkdirs , start_thread
import json , os , glob
from easy_utils_dev.FastQueue import FastQueue
from easy_utils_dev.debugger import DEBUGGER 
import zipfile
import tempfile
from collections import defaultdict


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
    
    def create_ept_tables_from_sql(self) :
        self.logger.info("Creating EPT Database Tables from SQL ...")
        db = self.Database()
        db.execute_script( f"{os.path.join(__LIBPATH__ , 'ept_sql' , 'create_ept_tables.sql')}")
        self.logger.info("Creating EPT Database Tables from SQL completed")


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
        all_tags = list(self.root.find_all())
        unique_table_names = list({str(tag.name) for tag in all_tags})
        grouped_by_table = defaultdict(list)
        for t in all_tags:
            grouped_by_table[str(t.name)].append(t)
        db = initDB()
        db.config_database_path(self.ept_db_path)
        table_columns_map = {}
        for table_name in unique_table_names:
            query = f"PRAGMA table_info({table_name})"
            cols = db.execute_dict(query)
            table_columns_map[table_name] = [c['name'] for c in cols]
        for table_name in unique_table_names:
            elements = grouped_by_table.get(table_name)
            if not elements:
                continue
            column_names = table_columns_map[table_name]
            rows = []
            rows_append = rows.append
            for tag in elements:
                template = dict.fromkeys(column_names, None)
                attrs = tag.attrs
                if attrs:
                    for key in column_names:
                        if key in attrs:
                            template[key] = attrs[key]
                parent = tag.parent
                if parent is not None:
                    template['parentId'] = parent.attrs.get('id')
                    template['parentTag'] = parent.name
                    if self.include_parent_attrs:
                        template['parentAttrs'] = json.dumps(parent.attrs)
                    grandparent = getattr(parent, 'parent', None)
                    if grandparent is not None:
                        template['grandparentId'] = grandparent.attrs.get('id')
                        template['grandparentTag'] = grandparent.name
                        if self.include_grantparent_attrs:
                            template['grandparentAttrs'] = json.dumps(grandparent.attrs)
                rows_append(template)
            if rows:
                db.insert_to_table_bulk(tableName=table_name , values=rows)
        self.logger.info("Creating EPT Rows completed")
                
    def parse(self) :
        if self.design_path.endswith('.ept') :
            self.extract_ept(self.design_path)

        with open(self.design_path , 'r' , encoding='utf-8') as file :
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

    def _create_crossconnections_table(self) : 
        query = f"""
        CREATE VIEW c_crossconnections AS
        SELECT DISTINCT 
            p.owner as wdmdemand, 
            sh.number || '-' || sm.physicalslot || '-L' || p.portnumber as physicalslot ,
            sh.type as shelftype ,
            sh.number as shelfid , 
            sm.physicalslot ,
            ch.deployedname,
            ch.name as eptname,
            s.name as sitename , 
            b.ot as boardtype ,
            rch.name as channelnumber
        FROM port p
        JOIN circuitpack cp ON p.parentId = cp.id
        JOIN shelf sh ON cp.parentId = sh.id
        JOIN site s ON sh.grandparentId = s.id
        JOIN OTtype b on b.OTtype = cp.type
        JOIN wdmdemand ch ON p.owner = ch.id AND ch.category = 'Trail'
        JOIN slot_mapping sm ON sh.type = sm.shelfType AND cp.slotid = sm.logicalSlot
        JOIN channel rch ON rch.num = CAST(REPLACE(REPLACE(ch.assignedChannels_primary, '[', ''), ']', '') AS INTEGER)
        WHERE ch.assignedChannels_primary IS NOT NULL
        AND rch.name IS NOT NULL
        AND cp.type IN (SELECT OTtype FROM OTtype WHERE otkind != 'alien' );
        """
        db = self.Database()
        db.execute_dict(query)

    def _create_ports_inventory(self) : 
        query = f"""
        CREATE VIEW c_port_inventory AS
        select 
            p.pluggable as moduletype, 
            p.pluggableapn as partnumber,
            p.portnumber,
            p.connectortype,
            cp.slotid,
            cp.id as eptpackid , 
            p.id as eptpid , 
            sh.id as eptshid , 
            s.id as eptsid , 
            sh.number as shelfid,
            sm.physicalslot,
            s.name as sitename,
            CASE 
                WHEN p.connectortype LIKE 'Line%' 
                    THEN sh.number || '-' || sm.physicalslot || '-L' || p.portnumber
                WHEN p.connectortype LIKE 'Client%' 
                    THEN sh.number || '-' || sm.physicalslot || '-C' || p.portnumber
                WHEN p.connectortype LIKE '%VOA%' 
                    THEN sh.number || '-' || sm.physicalslot || '-VA' || p.portnumber
                ELSE NULL
            END as custom_portname ,
            CASE 
                WHEN p.pluggable IS NULL AND physicalslot IS NOT NULL  AND p.pluggableapn is NULL
                    THEN 'free'
                ELSE 'busy'
            END as portstatus
        from port p
        JOIN circuitpack cp ON p.parentId = cp.id 
        JOIN shelf sh ON cp.parentId = sh.id
        JOIN site s ON sh.grandparentId = s.id
        JOIN slot_mapping sm ON sh.type = sm.shelfType AND cp.slotid = sm.logicalSlot
        JOIN OTtype ot ON ot.OTtype = cp.type 
        WHERE ( p.connectortype IS NOT NULL ) ;
        """
        db = self.Database()
        db.execute_dict(query)

    def _create_enhanced_dirs(self) : 
        query = f"""
        CREATE VIEW c_enhanced_dirs AS
        select DISTINCT
        line.id as eptlineid , 
        line.span as spanid , 
        site.id as eptsitenameid ,
        spn.name as eptsegementname , 
        line.wdmlink as wdmlinkid ,
        cp.type as boardtype ,
        sh.type as shelftype,
        sp.physicalslot as slot ,
        sh.number as shelfid ,
        site.name as sitename ,
        segt.id as segementid , 

        CASE
            WHEN segt2.asite = site.id THEN site_b.name
            WHEN segt2.bsite = site.id THEN site_a.name
        END AS farsitename,

        CASE 
            WHEN segtinfo.orient = 'AB' AND segt2.asite = site.id THEN segtinfo.dist
            WHEN segtinfo.orient = 'AB' AND segt2.bsite = site.id THEN segtinfo.dist
            WHEN segtinfo.orient = 'BA' AND segt2.asite = site.id THEN segtinfo.dist
            WHEN segtinfo.orient = 'BA' AND segt2.bsite = site.id THEN segtinfo.dist
        END AS distance ,
        sh.number || "-" || sp.physicalSlot as fullslot 
        from line 
        JOIN circuitpack cp ON cp.wdmline = line.id AND ( cp.packIDRef IS NOT NULL OR cp.type = oa.OAtype )
        JOIN site on site.id = sh.grandparentId
        JOIN OAtype as oa
        JOIN shelf sh ON sh.id = cp.parentId
        JOIN slot_mapping sp on sp.logicalSlot = cp.slotid  AND sh.type = sp.shelftype
        JOIN span spn ON spn.id = line.span AND spn.ashelfset IS NOT NULL
        JOIN segt ON segt.grandparentId = spn.id 
        JOIN segt segt2 ON segt.id = segt2.id AND segt2.asite IS NOT NULL
        JOIN segtinfo ON segtinfo.parentId = segt.id 
        JOIN site AS site_a ON site_a.id = segt2.asite
        JOIN site AS site_b ON site_b.id = segt2.bsite
        GROUP BY line.id ;

        """
        db = self.Database()
        db.execute_dict(query)

    def _create_card_inventory(self) : 
        query = f"""
        CREATE VIEW c_card_inventory AS
        SELECT DISTINCT 
            sh.number || '-' || pack.physicalslot AS slot,
            sh.number AS shelfid, 
            pack.physicalslot,
            s.name AS sitename,
            pack.apn,
            COALESCE(ott.ot, pack.type) AS boardname,
            pack.source_table
        FROM (
            -- Circuitpack → logicalSlot → physicalslot via slot_mapping
            SELECT cp.id,
                cp.parentId,
                sm.physicalslot,
                cp.type,
                cp.apn,
                'circuitpack' AS source_table
            FROM circuitpack cp
            JOIN shelf sh ON cp.parentId = sh.id
            JOIN slot_mapping sm 
                ON sh.type = sm.shelfType 
                AND cp.slotid = sm.logicalSlot

            UNION ALL

            -- Commonpack → already has physicalslot
            SELECT id,
                parentId,
                physicalslot,
                type,
                apn,
                'commonpack' AS source_table
            FROM commonpack
        ) pack
        JOIN shelf sh 
            ON pack.parentId = sh.id
        JOIN site s 
            ON sh.grandparentId = s.id
        LEFT JOIN OAtype ota 
            ON ota.OAtype = pack.type
        LEFT JOIN OTtype ott 
            ON ott.OTtype = pack.type;
        """
        db = self.Database()
        db.execute_dict(query)

    def _create_shelf_inventory(self) : 
        query = f"""
        CREATE VIEW c_shelf_info AS
        SELECT 
            sh.type AS  shelftype ,
            sh.number AS shelfnumber,
            sh.apn AS partnumber ,
            st.name AS sitename
        FROM shelf sh
        JOIN site st ON st.id = sh.grandparentId
        WHERE sh.number != 0
        UNION ALL
        SELECT 
            cp.type AS  shelftype ,
            cp.dcmpseudoshelf AS shelfnumber,
            cp.apn AS partnumber ,
            st.name as sitename 
        FROM circuitpack cp
        JOIN shelf sh ON sh.id = cp.parentId
        JOIN site st ON sh.grandparentId = st.id 
        WHERE cp.dcmpseudoshelf IS NOT NUll ;
        """
        db = self.Database()
        db.execute_dict(query)

    def _create_site_tmp_table(self) : 
        query = f"""
        CREATE TABLE c_tmp_site_view AS
        SELECT * FROM site;
        """
        db = self.Database()
        db.execute_dict(query)

    def convert_design(self , drop_cols=[] ) :
        start = getTimestamp()
        db = self.Database()
        self.parse()
        self.create_ept_tables_from_sql()
        self.create_ept_rows()
        # db.execute_script(f"{os.path.join(__LIBPATH__ , 'ept_sql' , 'create_dirs.sql')}")
        a = start_thread(self._create_v_dirs , daemon=True)
        b = start_thread(self._create_crossconnections_table , daemon=True)
        c = start_thread(self._create_card_inventory , daemon=True)
        d = start_thread(self._create_shelf_inventory , daemon=True)
        s = start_thread(self._create_site_tmp_table , daemon=True)
        s = start_thread(self._create_ports_inventory , daemon=True)
        s = start_thread(self._create_enhanced_dirs , daemon=True)
        a.join() ; b.join() ; c.join() ; d.join() ; s.join()
        
        end = getTimestamp()
        if os.path.exists(self.tmp_design_path) :
            os.remove(self.tmp_design_path)
        self.logger.info(f"Design converted in {round((end - start)/60 , 2)} mins")

    def get_all_dirs(self, filter_source_ne=None) : 
        db = self.Database()
        packs = self.get_all_amplifiers()
        _packs = []
        for pack in packs : 
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