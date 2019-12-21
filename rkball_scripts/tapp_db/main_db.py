import re


def load(path):
    text = ''
    statement = "INSERT INTO `tapp_companylog` VALUES(NULL, {0}, 10,'Auto-Import from 2018-09-12'," \
                " 48.3339080, 16.2169630, '[]', 1, NOW(), 1, NOW());\n\r"
    sql = "INSERT INTO `tapp_companylog`(`id`, `company`, `type`, `message`, `latitude`, `longitude`, `data`, `created_by`, `created_when`, `acknowledged_by`, `acknowledged_when`) " \
          "VALUES (NULL, {0}, 10, 'Auto-Import from 2018-08-29', 48.3339080, 16.2169630, '[]', 1, NOW(), 1, NOW()); \n\r"
    with open(path, 'r') as f:
        for r in f.readlines():
            if r.strip() != '' and not any(re.findall(r"[a-zA-Z]*", r)):
                text = text + sql.format(re.findall(r'"(.*)"', r)[0].strip())
    print(text)
    with open('nsql.txt', 'w') as f:
        f.write(text)


load('tapp_companylog.csv')



