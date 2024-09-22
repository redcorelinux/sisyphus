#!usr/bin/python3

def start(filter, cat='', pn='', desc=''):
    NOVIRT = "AND cat NOT LIKE 'virtual'"
    SELECTS = {
        'all': f'''SELECT
                    i.category AS cat,
                    i.name as pn,
                    i.slot as ist,
                    i.version as iv,
                    IFNULL(a.version, 'alien') AS av,
                    d.description AS desc
                    FROM local_packages AS i LEFT OUTER JOIN remote_packages as a
                    ON i.category = a.category
                    AND i.name = a.name
                    AND i.slot = a.slot
                    LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                    WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}
                    UNION
                    SELECT
                    a.category AS cat,
                    a.name as pn,
                    a.slot as ast,
                    IFNULL(i.version, 'None') AS iv,
                    a.version as av,
                    d.description AS desc
                    FROM remote_packages AS a LEFT OUTER JOIN local_packages AS i
                    ON a.category = i.category
                    AND a.name = i.name
                    AND a.slot = i.slot
                    LEFT JOIN remote_descriptions AS d ON a.name = d.name AND a.category = d.category
                    WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}''',
        'installed': f'''SELECT
                    i.category AS cat,
                    i.name AS pn,
                    i.slot as ist,
                    i.version AS iv,
                    a.version as av,
                    d.description AS desc
                    FROM local_packages AS i
                    LEFT JOIN remote_packages AS a
                    ON i.category = a.category
                    AND i.name = a.name
                    AND i.slot = a.slot
                    LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                    WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}''',
        'alien': f'''SELECT
                    i.category AS cat,
                    i.name AS pn,
                    i.slot as ist,
                    i.version as iv,
                    IFNULL(a.version, 'alien') AS av,
                    d.description AS desc
                    FROM local_packages AS i
                    LEFT JOIN remote_packages AS a
                    ON a.category = i.category
                    AND a.name = i.name
                    AND a.slot = i.slot
                    LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                    WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}
                    AND av IS 'alien' ''',
        'available': f'''SELECT
                    a.category AS cat,
                    a.name AS pn,
                    a.slot as ast,
                    i.version as iv,
                    a.version AS av,
                    d.description AS desc
                    FROM remote_packages AS a
                    LEFT JOIN local_packages AS i
                    ON a.category = i.category
                    AND a.name = i.name
                    AND a.slot = i.slot
                    LEFT JOIN remote_descriptions AS d ON a.name = d.name AND a.category = d.category
                    WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}
                    AND iv IS NULL''',
        'upgradable': f'''SELECT
                    i.category AS cat,
                    i.name AS pn,
                    i.slot as ist,
                    i.version as iv,
                    a.version AS av,
                    d.description AS desc
                    FROM local_packages AS i
                    INNER JOIN remote_packages AS a
                    ON i.category = a.category
                    AND i.name = a.name
                    AND i.slot = a.slot
                    LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                    WHERE cat LIKE '%{cat}%' AND pn LIKE '%{pn}%' AND desc LIKE '%{desc}%' {NOVIRT}
                    AND iv <> av'''
    }

    return SELECTS[filter]

