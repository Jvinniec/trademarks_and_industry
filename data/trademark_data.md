# Trademark Filing Data
The trademark filing data can be downloaded from the United States Patents and Trademarks Office (USPTO) here:
* Historical: https://developer.uspto.gov/product/trademark-annual-xml-applications
* Daily: https://developer.uspto.gov/product/trademark-daily-xml-file-tdxf-applications#product-files


# XML format
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
        </case-file>
        <!-- ... additional case files ... -->
      </action-keys>
    </file-segments>
  </application-information>
</trademark-applications-daily>
```

The following data are expected to be extracted from each filing:
* filing-date: Date on which the trademark application was filed
* serial-number: Unique identification number associated with the trademark
* mark-identification: Short name for the trademark
* case-file-statement/text: Short description of the trademark (could have more than one)
* classification/primary-code: Nice classification associated with the trademark (could be more than 1) 
