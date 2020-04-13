The data used in this project is broken into 

# Trademark Filing Data
The trademark filing data can be downloaded from the United States Patents and Trademarks Office (USPTO) here:
* Historical: https://developer.uspto.gov/product/trademark-annual-xml-applications
* Daily: https://developer.uspto.gov/product/trademark-daily-xml-file-tdxf-applications#product-files


## XML format
The data that will be extracted for each trademark filing is found in each file based on the following XML file structure.
```xml
<trademark-applications-daily>
  <application-information>
    <file-segments>
      <action-keys>

        <case-file>
          <serial-number>######</serial-number>
          <case-file-header>
            <filing-date>YYYYMMDD</filing-date>
            <registration-date>YYYYMMDD</registration-date>
            <status-code>###</status-code>
            <mark-identification>TEXT</mark-identification>
          </case-file-header>
          <case-file-statements>
            <case-file-statement>
              <text>DESCRIPTION TEXT</text>
            </case-file-statement>
            <!-- ... additional statements ... -->
          <classifications>
            <classification>
              <primary-code>###</primary-code>
            </classification>
            <!-- ... additional classifications ... -->
          </classifications>
          <case-file-owners>
            <case-file-owner>
              <!-- ... Filer information -->
              <city>New York</city>
              <state>NY</state>
              <!-- alternatively: country code -->
            </case-file-owner>
            <!-- additional case-file-owner groups -->
          </case-file-owners>
        </case-file>

        <!-- ... additional case files ... -->

      </action-keys>
    </file-segments>
  </application-information>
</trademark-applications-daily>
```

The following data are expected to be extracted from each filing:
* filing-date: Date on which the trademark application was filed
* registration-date: Date the trademark was officially registered
* status-code: Current status of the trademark
* serial-number: Unique identification number associated with the trademark
* mark-identification: Short name for the trademark
* case-file-statement/text: Short description of the trademark (could have more than one)
* classification/primary-code: List of Nice classifications associated with the trademark
* case-file-owner:
  * city, state, country


# Nice Classifications
The International Classification of Goods and Services (a.k.a. Nice Classification) identifies 45 groups into which a trademark may be classified.
* [Nice Classification details](https://www.wipo.int/classifications/nice/nclpub/en/fr/?explanatory_notes=show&lang=en&menulang=en&notion=class_headings&version=20200101) (as of Jan. 1, 2020)

For a list of Nice classifications, see [help_files/nice_classifications.csv](help_files/nice_classifications.csv).

For a list of industries associated with each Nice classification, see [help_files/nice_industry.csv](help_files/nice_industry.csv)

