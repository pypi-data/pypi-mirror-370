#!/usr/bin/env python
"""mysql manipulation of dns records"""

import ipaddress

from waflibs import dns, domain, error, log, shell

default_bind_dir = "/etc/bind"

logger = log.logger().get_logger()


def increment_ips(
    db,
    ipv6_address,
    ip_address,
    no_auto_ipv6_address,
    no_auto_ip_address,
    ignored_ips,
):
    if no_auto_ipv6_address:
        logger.debug("ipv6 address manually set.")
        logger.debug("not auto incrementing ipv6 address.")
        logger.debug("ipv6 address being used: {}".format(ipv6_address))
    else:
        logger.debug("ipv6 address not manually set.")
        logger.debug("auto incrementing ipv6 address.")
        command = "SELECT INET6_NTOA(max(ipv6)) FROM numeric_records \
                WHERE INET6_NTOA(ipv6) LIKE '2607:5300:60:3b25%';"
        logger.debug("command to execute: {}".format(command))
        cursor = db.cursor()
        cursor.execute(command)

        lowest_ipv6_address = cursor.fetchone()[0]
        cursor.close()

        logger.debug("lowest ipv6 address: {}".format(lowest_ipv6_address))
        if lowest_ipv6_address:
            ipv6_address = str(ipaddress.ip_address(lowest_ipv6_address) + 1)
        else:
            ipv6_address = None

    if no_auto_ip_address:
        logger.debug("ip address manually set.")
        logger.debug("not auto incrementing ip address.")
        logger.debug("ip address being used: {}".format(ip_address))
    else:
        logger.debug("ip address not manually set.")

        if ignored_ips:
            logger.debug("ignored ips array: {}".format(ignored_ips))
            ignored_ips_string = " ".join(
                [f"AND INET_NTOA(ip) NOT LIKE '{ii}.%'" for ii in ignored_ips]
            )[3:]
            ignored_ips_string = f"WHERE {ignored_ips_string}"
            logger.debug("ignored ip string: {}".format(ignored_ips_string))
        else:
            ignored_ips_string = ""

        min_count = f"SELECT MIN(cnt) INTO @min FROM (SELECT COUNT(*) cnt \
                FROM numeric_records {ignored_ips_string} GROUP BY ip) t;"

        min_ip = "SELECT INET_NTOA(t1.ip) FROM numeric_records t1 JOIN \
                (SELECT ip FROM numeric_records GROUP BY ip \
                HAVING COUNT(*) = @min) t2 ON t1.ip = t2.ip;"

        logger.debug("command to execute: {}".format(min_count))
        cursor = db.cursor(buffered=True)
        cursor.execute(min_count)
        logger.debug("command to execute: {}".format(min_ip))
        cursor.execute(min_ip)

        lowest_ip_address = cursor.fetchone()[0]
        cursor.close()

        logger.debug("least used ip address: {}".format(lowest_ip_address))
        if lowest_ip_address:
            ip_address = str(lowest_ip_address)
        else:
            ip_address = None

        logger.debug("auto incrementing ip address.")

    return ipv6_address, ip_address


def add_dns_to_mysql(
    db,
    hostname,
    ignored_ips=None,
    domains=None,
    content=None,
    record_type=None,
    ipv6_address=None,
    ip_address=None,
    priority=0,
    ttl=0,
    proxied=True,
    wikipedia_link=None,
    no_auto_ip_address=False,
    no_auto_ipv6_address=False,
    dry_run=False,
    public=False,
):
    if not hostname:
        message = "you must specify a hostname"
        logger.error(message)

        raise error.ValidationError(message)

    if not record_type or record_type == "AAAA" or record_type == "A":
        ipv6_address, ip_address = increment_ips(
            db,
            ipv6_address,
            ip_address,
            no_auto_ipv6_address,
            no_auto_ip_address,
            ignored_ips,
        )

    if wikipedia_link:
        wikipedia_link = wikipedia_link.strip()
        logger.debug("wikipedia link: {}".format(wikipedia_link))
        if "wikipedia" not in wikipedia_link:
            raise Exception("not a wikipedia link")

        command = "INSERT INTO dbm_hostnames (hostname, url) VALUES \
                ('{}', '{}');".format(
            hostname, wikipedia_link
        )
        logger.debug("command to execute: {}".format(command))
        if dry_run:
            logger.info("would execute mysql command")

            result = -1
        else:
            logger.debug("executing mysql command")
            cursor = db.cursor()
            result = cursor.execute(command)
            cursor.close()

    logger.debug("domains: {}".format(domains))
    if domains is None:
        if public:
            actual_domains = ["ALL_PUBLIC"]
        else:
            actual_domains = ["ALL_PRIVATE"]
    else:
        actual_domains = domains
    logger.debug("actual domains: {}".format(actual_domains))
    for domain in actual_domains:
        if record_type:
            logger.debug(f"record type orig: {record_type}")
            record_type = record_type.upper()
            logger.debug(f"record type: {record_type}")
            if content:
                content = content.strip()
                logger.debug("content: {}".format(content))
                priority = priority
                logger.debug("record priority: {}".format(priority))

                command = "INSERT INTO non_numeric_records (name, domain, \
                        type, content, priority, ttl, proxied) \
                        VALUES ('{}', '{}', '{}', '{}', {}, {}, {});".format(
                    hostname,
                    domain,
                    record_type,
                    content,
                    int(priority),
                    int(ttl),
                    int(proxied),
                )

                dupe_command = "SELECT * FROM non_numeric_records \
                        WHERE name = '{}' AND domain = '{}' \
                        AND type = '{}' AND content = '{}';".format(
                    hostname,
                    domain,
                    record_type,
                    content,
                )
            else:
                raise RuntimeError("you must specify content for this type")
        else:
            if (ip_address and ipv6_address) or (not ip_address and not ipv6_address):
                command = "INSERT INTO numeric_records (hostname, domain, ip, \
                        ipv6, proxied, ttl) VALUES ('{}', '{}', \
                        INET_ATON('{}'), INET6_ATON('{}'), {}, {});".format(
                    hostname,
                    domain,
                    ip_address,
                    ipv6_address,
                    int(proxied),
                    ttl,
                )

                dupe_command = "SELECT * FROM numeric_records \
                        WHERE hostname = '{}' AND domain = '{}' \
                        AND ip = INET_ATON('{}') \
                        AND ipv6 = INET6_ATON('{}');".format(
                    hostname,
                    domain,
                    ip_address,
                    ipv6_address,
                )
            elif ip_address and not ipv6_address:
                command = "INSERT INTO numeric_records \
                        (hostname, domain, ip, ipv6, proxied, ttl) \
                        VALUES ('{}', '{}', INET_ATON('{}'), NULL, \
                        {}, {});".format(
                    hostname,
                    domain,
                    ip_address,
                    int(proxied),
                    ttl,
                )

                dupe_command = "SELECT * FROM numeric_records \
                        WHERE hostname = '{}' AND domain = '{}' \
                        AND ip = INET_ATON('{}');".format(
                    hostname, domain, ip_address
                )
            elif ipv6_address and not ip_address:
                command = "INSERT INTO numeric_records \
                        (hostname, domain, ip, ipv6, proxied, ttl) \
                        VALUES ('{}', '{}', NULL, INET6_ATON('{}'), \
                        {}, {});".format(
                    hostname, domain, ipv6_address, int(proxied), ttl
                )

                dupe_command = "SELECT * FROM numeric_records \
                        WHERE hostname = '{}' AND domain = '{}' \
                        AND ipv6 INET6_ATON('{}');".format(
                    hostname,
                    domain,
                    ipv6_address,
                )
            else:
                raise RuntimeError("This should never happen")
        if dry_run:
            logger.info("would execute mysql command")

            results = -1
        else:
            duplicate = False
            logger.debug("executing mysql command")
            cursor = db.cursor(buffered=True, dictionary=True)

            special_types = ["CNAME"]
            if record_type in special_types:
                dupe_command = "SELECT * FROM non_numeric_records \
                        WHERE name = '{}' AND domain = '{}' \
                        AND type = '{}';".format(
                    hostname, domain, record_type
                )
            logger.debug("check duplicate command: {}".format(dupe_command))
            cursor.execute(dupe_command)
            results = cursor.fetchone()
            cursor.close()
            if results:
                duplicate = True
            if duplicate:
                if record_type in special_types:
                    command = "UPDATE non_numeric_records \
                            SET content = '{content}', \
                            name = '{name}', \
                            domain = '{domain}', \
                            type = '{record_type}', \
                            priority = {priority}, \
                            ttl = {ttl}, \
                            proxied = {proxied} \
                            WHERE name = '{name}' AND \
                            domain = '{domain}' AND \
                            type = '{record_type}' AND \
                            priority = {priority} AND \
                            ttl = {ttl} AND \
                            proxied = {proxied};".format(
                        name=hostname,
                        domain=domain,
                        record_type=record_type,
                        content=content,
                        priority=int(priority),
                        ttl=int(ttl),
                        proxied=int(proxied),
                    )
                    logger.debug("command to execute: {}".format(command))
                    cursor = db.cursor()
                    logger.debug("executing mysql command")
                    cursor.execute(command)
                    cursor.close()
                else:
                    logger.info("record already exists. not doing anything")
            else:
                logger.debug("command to execute: {}".format(command))
                cursor = db.cursor()
                logger.debug("executing mysql command")
                cursor.execute(command)
                cursor.close()

        if ipv6_address:
            ipv6_address = str(ipaddress.ip_address(ipv6_address) + 1)

    logger.debug("all db results: {}".format(str(cursor)))

    db.commit()


def generate_bind_file(
    db,
    zones,
    bind_dir=default_bind_dir,
    serial=None,
    dry_run=False,
):
    cursor = db.cursor()

    if zones:
        if isinstance(zones, str):
            domains = [zones]
        else:
            domains = zones
    else:
        command = "SELECT DISTINCT domain from non_numeric_records;"
        cursor.execute(command)
        nnr_domains = tuple(map(lambda l: l[0], cursor.fetchall()))
        command = "SELECT DISTINCT domain from numeric_records;"
        cursor.execute(command)
        nr_domains = tuple(map(lambda l: l[0], cursor.fetchall()))
        domains = set(nnr_domains + nr_domains)
    logger.debug("distinct domains to generate: {}".format(str(domains)))

    if serial:
        serial_number = int(serial)
    else:
        serial_number = dns.bind.generate_serial_number()

    for domain in domains:
        dns.bind.generate_bind_file(
            get_records(cursor, domain),
            domain,
            bind_dir=bind_dir,
            serial_number=serial_number,
            dry_run=dry_run,
            template_file_name="{}/db.template".format(bind_dir),
            domain_template_file_name="{}/db.{}.template".format(bind_dir, domain),
        )

    for shared_name in ["ALL_PRIVATE", "ALL_PUBLIC"]:
        dns.bind.generate_bind_file(
            get_records(cursor, shared_name, shared=True),
            shared_name,
            bind_dir=bind_dir,
            zone_file_name="db.shared.{}".format(shared_name.split("_")[-1].lower()),
            serial_number=serial_number,
            dry_run=dry_run,
        )


def get_records(cursor, domain, shared=False):
    logger.debug("starting to get records for {}".format(domain))

    # get all records from the db
    command = "SELECT * FROM non_numeric_records WHERE domain = '{}';".format(domain)
    logger.debug("about to execute sql: {}".format(command))
    cursor.execute(command)
    nnr_results = cursor.fetchall()
    command = "SELECT hostname,domain,INET_NTOA(ip),INET6_NTOA(ipv6),proxied,ttl FROM \
        numeric_records WHERE domain = '{}';".format(
        domain
    )
    logger.debug("about to execute sql: {}".format(command))
    cursor.execute(command)
    nr_results = cursor.fetchall()
    all_results = {"numeric": nr_results, "non_numeric": nnr_results}
    logger.debug("all db results: {}".format(str(all_results)))

    all_records = []
    while all_results:
        result_type, results = all_results.popitem()
        logger.debug(f"result type: {result_type}")

        if result_type == "numeric":
            for row in results:
                logger.debug("numeric row result: {}".format(str(row)))

                short_hostname, domain, ip, ipv6, proxied, ttl = row

                logger.debug("original hostname: {}".format(short_hostname))
                hostname = domain.convert_origin(short_hostname, domain, shared)

                logger.debug("hostname: {}, domain: {}".format(hostname, domain))
                logger.debug("ip: {}, ipv6: {}".format(ip, ipv6))

                if ip:
                    all_records.append(
                        {
                            "name": hostname,
                            "type": "A",
                            "content": ip,
                            "proxied": proxied,
                        }
                    )
                if ipv6:
                    all_records.append(
                        {
                            "name": hostname,
                            "type": "AAAA",
                            "content": ipv6,
                            "proxied": proxied,
                        }
                    )
        elif result_type == "non_numeric":
            for row in results:
                logger.debug("non-numeric row result: {}".format(str(row)))

                (
                    _id,
                    short_name,
                    domain,
                    record_type,
                    priority,
                    content,
                    proxied,
                    ttl,
                ) = row

                logger.debug("original name: {}".format(short_name))
                name = domain.convert_origin(short_name, domain, shared)

                logger.debug(
                    "name: {}, domain: {}, record_type: {},".format(
                        name, domain, record_type
                    )
                )
                logger.debug("content: {}, proxied: {}".format(content, proxied))

                all_records.append(
                    {
                        "name": name,
                        "type": record_type,
                        "content": content,
                        "proxied": proxied,
                    }
                )
        else:
            raise Exception("this should not happen")

    logger.debug("finished getting records for {}".format(domain))

    return all_records
