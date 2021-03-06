#!/usr/bin/env python3
# License: CC0 https://creativecommons.org/publicdomain/zero/1.0/

import csv
import requests
import re

def mysql_quote(x):
    '''
    Quote the string x using MySQL quoting rules. If x is the empty string,
    return "NULL". Probably not safe against maliciously formed strings, but
    whatever; our input is fixed and from a basically trustable source..
    '''
    if not x:
        return "NULL"
    x = x.replace("\\", "\\\\")
    x = x.replace("'", "''")
    x = x.replace("\n", "\\n")
    return "'{}'".format(x)

def main():
    with open("wellcome-grants-awarded-2000-2016.csv", "r") as f:
        reader = csv.DictReader(f)

        first = True

        print("""insert into donations (donor, donee, amount, donation_date,
        donation_date_precision, donation_date_basis, cause_area, url,
        donor_cause_area_url, notes, affected_countries,
        affected_regions, amount_original_currency, original_currency,
        currency_conversion_date, currency_conversion_basis) values""")

        for row in reader:
            donee = row['Organisation'].strip()
            if donee == "No Organisation":
                donee = row['Lead Applicant'].strip()
            # There is also "Financial year", "Start Date", and "End Date"
            day, month, year = row['Date of Award'].split('/')
            donation_date = year + "-" + month + "-" + day
            amount_original = float(row[' Amount awarded (£) '].replace(",", "")
                                                               .strip())
            amount = gbp_to_usd(amount_original, donation_date)
            notes = row['Project title']
            country = row['Country']

            # Some of the countries in the spreadsheet is in all caps, so fix
            # those
            if country == country.upper():
                country = " ".join(map(lambda x: x[0] + x[1:].lower(),
                                       country.strip().split()))
            region = row['Region']

            # This is to make sure that each country/region is just a single
            # location rather than multiple. (If there are multiple, we would
            # need to separate them by pipes, so passing this assertion allows
            # us to skip that step.)
            for loc in [country, region]:
                assert re.match(r"[A-Za-z ]+", loc), loc

            print(("    " if first else "    ,") + "(" + ",".join([
                mysql_quote("Wellcome Trust"),  # donor
                mysql_quote(donee),  # donee
                str(amount),  # amount
                mysql_quote(donation_date),  # donation_date
                mysql_quote("day"),  # donation_date_precision
                mysql_quote("donation log"),  # donation_date_basis
                mysql_quote("FIXME"),  # cause_area
                mysql_quote("https://wellcome.ac.uk/sites/default/files/wellcome-grants-awarded-2000-2016.xlsx"),  # url
                mysql_quote("FIXME"),  # donor_cause_area_url
                mysql_quote(notes),  # notes
                mysql_quote(country),  # affected_countries
                mysql_quote(region),  # affected_regions
                str(amount_original),  # amount_original_currency
                mysql_quote('GBP'),  # original_currency
                mysql_quote(donation_date),  # currency_conversion_date
                mysql_quote("Fixer.io"),  # currency_conversion_basis
            ]) + ")")
            first = False
        print(";")


def gbp_to_usd(gbp_amount, date):
    """Convert the GBP amount to USD."""
    r = requests.get("https://api.fixer.io/{}?base=USD".format(date))
    j = r.json()
    rate = j["rates"]["GBP"]
    return gbp_amount / rate


if __name__ == "__main__":
    main()
