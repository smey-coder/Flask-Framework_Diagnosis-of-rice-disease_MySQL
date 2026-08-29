# MySQL
1. for add column into table
ALTER TABLE tbl_preventions
ADD COLUMN priority INT NOT NULL DEFAULT 1
AFTER image;
# ----------
2.for show propity table all
DESCRIBE tbl_preventions;

#---------------------------------------------------
# ឯកសារបកស្រាយបញ្ហា និងដំណោះស្រាយ៖ ស្រមោលបង្កើត View បរាជ័យលើ Alwaysdata Cloud Database

ឯកសារនេះរៀបរាប់អំពីមូលហេតុ និងវិធីដោះស្រាយបញ្ហាបង្កើត SQL View 不រលូន ឬបាត់បង់ View នៅពេល Import ទិន្នន័យពី Local Host (XAMPP/WAMP) ទៅកាន់ Alwaysdata Cloud Database។

---

## 1. បញ្ហាដែលជួបប្រទះ (The Problems)

### បញ្ហាទី ១៖ បាត់ View ពេល Import ឬទាមទារសិទ្ធិ DEFINER
* **រោគសញ្ញា:** View មាននៅលើ Local Database ប៉ុន្តែពេល Import ចូល Alwaysdata ស្រាប់តែបាត់ View ឬកើតមាន Error ទាក់ទងនឹងសិទ្ធិ (`Access denied; you need ... privilege`).
* **មូលហេតុ:** SQL Dump File ដែល Export ចេញពី Local ជាប់កូដ `DEFINER=`root`@`localhost``។ Alwaysdata បដិសេធសិទ្ធិ `root` នេះ។

### បញ្ហាទី ២៖ Error `#1146 - Table 'alwaydata_rdds_db.diagnosis' doesn't exist`
* **រោគសញ្ញា:** ប្រព័ន្ធប្រាប់ថា រកមិនឃើញ តារាង (Table) សម្រាប់បង្កើត View ឡើយ។
* **មូលហេតុ:** 
  1. ឈ្មោះ Table នៅលើ Linux Cloud (Alwaysdata) ប្រកាន់អក្សរតូច-ធំ (Case-sensitive)។
  2. ឈ្មោះ Table ពិតប្រាកដមាន Prefix (ឧទាហរណ៍៖ មាន `tbl_` នៅខាងមុខ ដូចជា `tbl_diagnosis_history`)។

### បញ្ហាទី ៣៖ Error `'alwaydata_rdds_db.view_diagnosis_history' is not of type 'VIEW'`
* **រោគសញ្ញា:** ប្រព័ន្ធស្គាល់ `view_diagnosis_history` ជា Table ធម្មតា មិនមែនជា View ឡើយ។
* **មូលហេតុ:** ពេល Import បរាជ័យត្រឹម `DEFINER`, phpMyAdmin បានបង្កើត "Stand-in Table" (តារាងបណ្តោះអាសន្ន) រក្សាទុក ប៉ុន្តែមិនទាន់បានប្តូរទៅជា View ពិតប្រាកដឡើយ។

---

## 2. ដំណោះស្រាយ (The Solution)

ដើម្បីដោះស្រាយបញ្ហានេះ ត្រូវលុប Stand-in Table ចាស់ចោល រួចបង្កើត View សារជាថ្មីដោយប្រើឈ្មោះ Table និង Column ត្រឹមត្រូវ ព្រមទាំងលុប `DEFINER` ចោល។

### កូដ SQL សម្រាប់ដោះស្រាយ (Fix Script):

```sql
-- ជំហានទី ១៖ លុប Table បណ្តោះអាសន្ន ឬ View ចាស់ដែលខូចចោល
DROP TABLE IF EXISTS `alwaydata_rdds_db`.`view_diagnosis_history`;
DROP VIEW IF EXISTS `alwaydata_rdds_db`.`view_diagnosis_history`;

-- ជំហានទី ២៖ បង្កើត View ថ្មីដោយប្រើឈ្មោះ Table ត្រឹមត្រូវ (tbl_) និងគ្មាន DEFINER
CREATE VIEW `alwaydata_rdds_db`.`view_diagnosis_history` AS
SELECT 
    d.id,
    d.user_id,
    d.created_at,
    u.full_name,
    dis.disease_name,
    dis.disease_type,
    d.severity_level,
    d.description,
    d.image,
    d.confidence
FROM tbl_diagnosis_history d
LEFT JOIN tbl_users u ON d.user_id = u.id
LEFT JOIN tbl_diseases dis ON d.disease_id = dis.id;