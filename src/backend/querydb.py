#!usr/bin/python3

def start(filter, cat='', pn='', desc=''):
    NOVIRT = "AND cat NOT LIKE 'virtual'"
    NO_DESC = "Alien package outside of Gentoo Linux/Redcore Linux"
    SELECTS = {
        'all': f'''SELECT
                    i.category AS cat,
                    i.name as pn,
                    i.slot as ist,
                    i.version as iv,
                    IFNULL(a.version, 'alien') AS av,
                    COALESCE(d.description, '{NO_DESC}') AS desc
                    FROM local_packages AS i LEFT OUTER JOIN remote_packages as a
                    ON i.category = a.category
                    AND i.name = a.name
                    AND i.slot = a.slot
                    LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                    WHERE i.category LIKE '%{cat}%' AND i.name LIKE '%{pn}%'
                    AND (COALESCE(d.description, '{NO_DESC}, ') LIKE '%{desc}%' OR d.description IS NULL) {NOVIRT}
                    UNION
                    SELECT
                    a.category AS cat,
                    a.name as pn,
                    a.slot as ast,
                    IFNULL(i.version, 'None') AS iv,
                    a.version as av,
                    COALESCE(d.description, '{NO_DESC}') AS desc
                    FROM remote_packages AS a LEFT OUTER JOIN local_packages AS i
                    ON a.category = i.category
                    AND a.name = i.name
                    AND a.slot = i.slot
                    LEFT JOIN remote_descriptions AS d ON a.name = d.name AND a.category = d.category
                    WHERE a.category LIKE '%{cat}%' AND a.name LIKE '%{pn}%'
                    AND (COALESCE(d.description, '{NO_DESC}') LIKE '%{desc}%' OR d.description IS NULL) {NOVIRT}''',
        'installed': f'''SELECT
                    i.category AS cat,
                    i.name AS pn,
                    i.slot as ist,
                    i.version AS iv,
                    a.version as av,
                    COALESCE(d.description, '{NO_DESC}') AS desc
                    FROM local_packages AS i
                    LEFT JOIN remote_packages AS a
                    ON i.category = a.category
                    AND i.name = a.name
                    AND i.slot = a.slot
                    LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                    WHERE i.category LIKE '%{cat}%' AND i.name LIKE '%{pn}%'
                    AND (COALESCE(d.description, '{NO_DESC}') LIKE '%{desc}%' OR d.description IS NULL) {NOVIRT}''',
        'alien': f'''SELECT
                    i.category AS cat,
                    i.name AS pn,
                    i.slot as ist,
                    i.version as iv,
                    IFNULL(a.version, 'alien') AS av,
                    COALESCE(d.description, '{NO_DESC}') AS desc
                    FROM local_packages AS i
                    LEFT JOIN remote_packages AS a
                    ON a.category = i.category
                    AND a.name = i.name
                    AND a.slot = i.slot
                    LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                    WHERE i.category LIKE '%{cat}%' AND i.name LIKE '%{pn}%'
                    AND (COALESCE(d.description, '{NO_DESC}') LIKE '%{desc}%' OR d.description IS NULL) {NOVIRT}
                    AND IFNULL(a.version, 'alien') = 'alien' ''',
        'available': f'''SELECT
                    a.category AS cat,
                    a.name AS pn,
                    a.slot as ast,
                    i.version as iv,
                    a.version AS av,
                    COALESCE(d.description, '{NO_DESC}') AS desc
                    FROM remote_packages AS a
                    LEFT JOIN local_packages AS i
                    ON a.category = i.category
                    AND a.name = i.name
                    AND a.slot = i.slot
                    LEFT JOIN remote_descriptions AS d ON a.name = d.name AND a.category = d.category
                    WHERE a.category LIKE '%{cat}%' AND a.name LIKE '%{pn}%'
                    AND (COALESCE(d.description, '{NO_DESC}') LIKE '%{desc}%' OR d.description IS NULL) {NOVIRT}
                    AND i.version IS NULL''',
        'upgradable': f'''SELECT
                    i.category AS cat,
                    i.name AS pn,
                    i.slot as ist,
                    i.version as iv,
                    a.version AS av,
                    COALESCE(d.description, '{NO_DESC}') AS desc
                    FROM local_packages AS i
                    INNER JOIN remote_packages AS a
                    ON i.category = a.category
                    AND i.name = a.name
                    AND i.slot = a.slot
                    LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                    WHERE i.category LIKE '%{cat}%' AND i.name LIKE '%{pn}%'
                    AND (COALESCE(d.description, '{NO_DESC}') LIKE '%{desc}%' OR d.description IS NULL) {NOVIRT}
                    AND i.version <> a.version'''
    }

    return SELECTS[filter]

