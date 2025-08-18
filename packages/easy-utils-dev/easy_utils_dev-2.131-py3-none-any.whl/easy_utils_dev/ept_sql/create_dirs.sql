BEGIN;

-- 1) Mapping table: (shelfType, logicalSlot) -> physicalSlot
CREATE TABLE IF NOT EXISTS slot_mapping (
  shelfType    TEXT    NOT NULL,
  logicalSlot  INTEGER NOT NULL,
  physicalSlot INTEGER NOT NULL,
  PRIMARY KEY (shelfType, logicalSlot)
);

-- Clean existing rows so script is idempotent without dialect-specific UPSERT
DELETE FROM slot_mapping;

-- PSS32 (32 slots)
INSERT INTO slot_mapping (shelfType, logicalSlot, physicalSlot) VALUES
('PSS32',1,2),('PSS32',2,20),('PSS32',3,3),('PSS32',4,21),
('PSS32',5,4),('PSS32',6,22),('PSS32',7,5),('PSS32',8,23),
('PSS32',9,6),('PSS32',10,24),('PSS32',11,7),('PSS32',12,25),
('PSS32',13,8),('PSS32',14,26),('PSS32',15,9),('PSS32',16,27),
('PSS32',17,10),('PSS32',18,28),('PSS32',19,11),('PSS32',20,29),
('PSS32',21,12),('PSS32',22,30),('PSS32',23,13),('PSS32',24,31),
('PSS32',25,14),('PSS32',26,32),('PSS32',27,15),('PSS32',28,33),
('PSS32',29,16),('PSS32',30,34),('PSS32',31,17),('PSS32',32,35);

-- PSS16II (16 slots)
INSERT INTO slot_mapping (shelfType, logicalSlot, physicalSlot) VALUES
('PSS16II',1,3),('PSS16II',2,13),('PSS16II',3,4),('PSS16II',4,14),
('PSS16II',5,5),('PSS16II',6,15),('PSS16II',7,6),('PSS16II',8,16),
('PSS16II',9,7),('PSS16II',10,17),('PSS16II',11,8),('PSS16II',12,18),
('PSS16II',13,9),('PSS16II',14,19),('PSS16II',15,10),('PSS16II',16,20);

-- PSS16 (same mapping as PSS16II)
INSERT INTO slot_mapping (shelfType, logicalSlot, physicalSlot) VALUES
('PSS16',1,3),('PSS16',2,13),('PSS16',3,4),('PSS16',4,14),
('PSS16',5,5),('PSS16',6,15),('PSS16',7,6),('PSS16',8,16),
('PSS16',9,7),('PSS16',10,17),('PSS16',11,8),('PSS16',12,18),
('PSS16',13,9),('PSS16',14,19),('PSS16',15,10),('PSS16',16,20);

-- PSS8 (8 slots)
INSERT INTO slot_mapping (shelfType, logicalSlot, physicalSlot) VALUES
('PSS8',1,2),('PSS8',2,8),('PSS8',3,3),('PSS8',4,9),
('PSS8',5,4),('PSS8',6,10),('PSS8',7,5),('PSS8',8,11);

-- 2) Helpful indexes
CREATE INDEX IF NOT EXISTS idx_circuitpack_parent     ON circuitpack(parentId);
CREATE INDEX IF NOT EXISTS idx_circuitpack_wdmline    ON circuitpack(wdmline);
CREATE INDEX IF NOT EXISTS idx_circuitpack_slotid     ON circuitpack(slotid);
CREATE INDEX IF NOT EXISTS idx_shelf_id               ON shelf(id);
CREATE INDEX IF NOT EXISTS idx_shelf_grandparent      ON shelf(grandparentId);
CREATE INDEX IF NOT EXISTS idx_shelf_type             ON shelf(type);
CREATE INDEX IF NOT EXISTS idx_line_id                ON "line"(id);
CREATE INDEX IF NOT EXISTS idx_line_span              ON "line"(span);
CREATE INDEX IF NOT EXISTS idx_site_id                ON site(id);

-- 3) View that reproduces get_all_dirs()
DROP VIEW IF EXISTS v_dirs;
CREATE VIEW v_dirs AS
SELECT
  src.name AS sourceNe,
  dst.name AS destinationNe,
  cp.type  AS board,
  sm.physicalSlot AS physicalslot,
  (sh.number || '/' || sm.physicalSlot) AS slot,
  sh.type AS shelfType,
  cp.id   AS circuitpack_id,
  sh.id   AS shelf_id,
  l1.span AS span_id,
  src.id  AS source_site_id,
  dst.id  AS destination_site_id
FROM circuitpack cp
JOIN shelf sh            ON sh.id = cp.parentId
JOIN site src            ON src.id = sh.grandparentId
JOIN "line" l1           ON l1.id = cp.wdmline
JOIN "line" l2           ON l2.span = l1.span AND l2.grandparentId <> sh.grandparentId
JOIN site dst            ON dst.id = l2.grandparentId
WHERE cp.packIDRef IS NOT NULL
  AND cp.type IN (
    SELECT packName FROM OAtype
    WHERE packName IS NOT NULL OR packName != ''
  );

COMMIT;