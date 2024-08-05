import re

def extract_modified_version(prompt):
    # 定义匹配SQL语句的正则表达式
    sql_pattern = re.compile(
        r"```sql(.*?)```|"
        r"\*\*Modified version:\*\*\s*```sql(.*?)```|"
        r"\*\*Modified version:\*\*\s*(.*?)(?=(\n\*\*|$))",
        re.DOTALL
    )
    # 在prompt中搜索匹配项
    match = sql_pattern.search(prompt)
    
    if match:
        # 返回匹配的SQL语句
        return match.group(1) or match.group(2) or match.group(3)
    else:
        return None

format1 = """
**Modified version:**
```sql
SELECT COUNT(*) FROM contacts INNER JOIN aspect_memberships ON contacts.id = aspect_memberships.contact_id WHERE aspect_memberships.aspect_id = 3;
```
"""

format2 = """
**Modified version:** 
SELECT COUNT(*) 
FROM `contacts` 
INNER JOIN `aspect_memberships` ON `contacts`.`id` = `aspect_memberships`.`contact_id` 
WHERE `aspect_memberships`.`aspect_id` = 3;
"""

format3 = """
```sql
SELECT COUNT(*) FROM contacts INNER JOIN aspect_memberships ON contacts.id = aspect_memberships.contact_id WHERE aspect_memberships.aspect_id = 3;
```
"""
format4 = """
```sql
SELECT COUNT(*) 
FROM `contacts` 
INNER JOIN `aspect_memberships` ON `contacts`.`id` = `aspect_memberships`.`contact_id` 
WHERE `aspect_memberships`.`aspect_id` = 3;
```
"""
format5 = """
**Modified version:** 
SELECT COUNT(*) FROM `contacts` INNER JOIN `aspect_memberships` ON `contacts`.`id` = `aspect_memberships`.`contact_id` WHERE `aspect_memberships`.`aspect_id` = 3;
"""

print("format 1", extract_modified_version(format1))
print("format 2", extract_modified_version(format2))
print("format 3", extract_modified_version(format3))
print("format 4", extract_modified_version(format4))
print("format 5", extract_modified_version(format5))