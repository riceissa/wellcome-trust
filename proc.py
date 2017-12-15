#!/usr/bin/env python3

import csv

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
        affected_regions) values""")

        for row in reader:
            donee = row['Organisation']
            # FIXME this is in pounds
            amount = row[' Amount awarded (£) '].replace(",", "").strip()
            # There is also "Financial year", "Start Date", and "End Date"
            day, month, year = row['Date of Award'].split('/')
            donation_date = year + "-" + month + "-" + day
            notes = row['Project title']
            country = row['Country']

            # Some of the countries in the spreadsheet is in all caps, so fix
            # those
            if country == country.upper():
                country = " ".join(map(lambda x: x[0] + x[1:].lower(),
                                       country.strip().split()))
            region = row['Region']

            print(("    " if first else "    ,") + "(" + ",".join([
                mysql_quote("Wellcome Trust"),  # donor
                mysql_quote(donee),  # donee
                amount,  # amount
                mysql_quote(donation_date),  # donation_date
                mysql_quote("day"),  # donation_date_precision
                mysql_quote("donation log"),  # donation_date_basis
                mysql_quote("FIXME"),  # cause_area
                mysql_quote("https://wellcome.ac.uk/sites/default/files/wellcome-grants-awarded-2000-2016.xlsx"),  # url
                mysql_quote("FIXME"),  # donor_cause_area_url
                mysql_quote(notes),  # notes
                mysql_quote(country),  # affected_countries
                mysql_quote(region),  # affected_regions
            ]) + ")")
            first = False
        print(";")


if __name__ == "__main__":
    main()
