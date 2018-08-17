"""
EDIFACT Parser
**************
Requires Python 3.6 or higher

Features
--------
- All encodings
- Version independent
- XML

Functions
---------
parse_edi(data: bytes)                -> list
make_edi(segments: list)              -> bytes
parse_xml(root: ElementTree.Element)  -> list
make_xml(segments: list)              -> ElementTree.Element
pretty_xml(root: ElementTree.Element) -> str

Experimental
------------
report(segments: list)                           -> None
make_edi_xml(segments: list, sd: dict, ed: dict) -> ElementTree.Element

Example message
---------------
>>> edi = b"UNA:+.? 'UNB+UNOY:3+INVALIDATORSTUDIO:1+BYTESREADER:1+20180630:1159+6002'UNH+SSDD1+ORDERS:D:03B:UN:EAN008'BGM+220+BKOD99+9'DTM+137:20180630:102'NAD+BY+31-424-2022::16'NAD+SU+34-093-1588::16'LIN+1+1+0764569104:IB'QTY+1:25'FTX+AFM+1++XPATH 2.0 PROGRAMMER?'S REFERENCE'LIN+2+1+0764569090:IB'QTY+1:25'FTX+AFM+1++XSLT 2.0 PROGRAMMER?'S REFERENCE'LIN+3+1+1861004656:IB'QTY+1:16'FTX+AFM+1++JAVA SERVER PROGRAMMING'LIN+4+1+0-19-501476-6:IB'QTY+1:10'FTX+AFM+1++TZUN TZU'UNS+S'CNT+2:4'UNT+22+SSDD1'UNZ+1+6002'"

Data-type
---------
>>> segments = parse_edi(edi)
>>> type(segments)
<class 'list'>

>>> pprint.pprint(segments)
[['UNA', [':', '+', '.', '?', ' ', "'"]],
 ['UNB',
  [['UNOY', '3'],
   ['INVALIDATORSTUDIO', '1'],
   ['BYTESREADER', '1'],
   ['20180630', '1159'],
   ['6002']]],
 ['UNH', [['SSDD1'], ['ORDERS', 'D', '03B', 'UN', 'EAN008']]],
 ['BGM', [['220'], ['BKOD99'], ['9']]],
 ['DTM', [['137', '20180630', '102']]],
 ['NAD', [['BY'], ['31-424-2022', '', '16']]],
 ['NAD', [['SU'], ['34-093-1588', '', '16']]],
 ['LIN', [['1'], ['1'], ['0764569104', 'IB']]],
 ['QTY', [['1', '25']]],
 ['FTX', [['AFM'], ['1'], [''], ["XPATH 2.0 PROGRAMMER'S REFERENCE"]]],
 ['LIN', [['2'], ['1'], ['0764569090', 'IB']]],
 ['QTY', [['1', '25']]],
 ['FTX', [['AFM'], ['1'], [''], ["XSLT 2.0 PROGRAMMER'S REFERENCE"]]],
 ['LIN', [['3'], ['1'], ['1861004656', 'IB']]],
 ['QTY', [['1', '16']]],
 ['FTX', [['AFM'], ['1'], [''], ['JAVA SERVER PROGRAMMING']]],
 ['LIN', [['4'], ['1'], ['0-19-501476-6', 'IB']]],
 ['QTY', [['1', '10']]],
 ['FTX', [['AFM'], ['1'], [''], ['TZUN TZU']]],
 ['UNS', [['S']]],
 ['CNT', [['2', '4']]],
 ['UNT', [['22'], ['SSDD1']]],
 ['UNZ', [['1'], ['6002']]]]

Indexing
--------
>>> segments[7]
['LIN', [['1'], ['1'], ['0764569104', 'IB']]]
>>> segment, elements = segments[7]
>>> segment
'LIN'
>>> elements
[['1'], ['1'], ['0764569104', 'IB']]

Index-Semantics
---------------
'IB' in 'LIN'-segment is code (7143) for ISBN.

segment                          elements[2][1] (7143)  <----------------------------------------------|
   |                                   |                                                               |
   |                                   |                                                               |
['LIN', [['1'], ['1'], ['0764569104', 'IB']]]                                                          |
                              |                                                                        |
                              |                                                                        |
                        elements[2][0] (7140)  <------------------------------------------------|      |
                                                                                                |      |
    LIN - Segment-table                                                                         |      |
    -------------------                                                                         |      |
    POS   CODE    NAME                                  M/C   REPEAT    REPRESENTATION          |      |
    ----------------------------------------------------------------------------------          |      |
    010   1082    LINE ITEM IDENTIFIER                  C     1         an..6                   |      |
    020   1229    ACTION CODE                           C     1         an..3                   |      |
    030   C212    ITEM NUMBER IDENTIFICATION            C     1                                 |      |
          7140    Item identifier                       C               an..35          <-------|      |
|------>  7143    Item type identification code         C               an..3           <---------------
|         1131    Code list identification code         C               an..17
|         3055    Code list responsible agency code     C               an..3
|   040   C829    SUB-LINE INFORMATION                  C     1
|         5495    Sub-line indicator code               C               an..3
|         1082    Line item identifier                  C               an..6
|   050   1222    CONFIGURATION LEVEL NUMBER            C     1         n..2
|   060   7083    CONFIGURATION OPERATION CODE          C     1         an..30
|
|
|   7143 - Code-table
|   -----------------
|   ...
|-> IB    ISBN (International Standard Book Number)
                  Self explanatory.

    IN    Buyer's item number
                  The item number has been allocated by the buyer.
    ...

>>> isbns = [elements[2][0] for segment, elements in segments if segment == 'LIN' and elements[2][1] == 'IB']
>>> isbns
['0764569104', '0764569090', '1861004656', '0-19-501476-6']

Formatting
----------
>>> edmoji = make_edi(segments,
...                   component_separator='✉',
...                   dataelement_separator='☺',
...                   decimal_mark='☣',
...                   release_char='☎',
...                   segment_terminator='❤',
...                   with_newline=True)

>>> print(edmoji.decode('utf8'))
UNA✉☺☣☎ ❤
UNB☺UNOY✉3☺INVALIDATORSTUDIO✉1☺BYTESREADER✉1☺20180630✉1159☺6002❤
UNH☺SSDD1☺ORDERS✉D✉03B✉UN✉EAN008❤
BGM☺220☺BKOD99☺9❤
DTM☺137✉20180630✉102❤
NAD☺BY☺31-424-2022✉✉16❤
NAD☺SU☺34-093-1588✉✉16❤
LIN☺1☺1☺0764569104✉IB❤
QTY☺1✉25❤
FTX☺AFM☺1☺☺XPATH 2.0 PROGRAMMER'S REFERENCE❤
LIN☺2☺1☺0764569090✉IB❤
QTY☺1✉25❤
FTX☺AFM☺1☺☺XSLT 2.0 PROGRAMMER'S REFERENCE❤
LIN☺3☺1☺1861004656✉IB❤
QTY☺1✉16❤
FTX☺AFM☺1☺☺JAVA SERVER PROGRAMMING❤
LIN☺4☺1☺0-19-501476-6✉IB❤
QTY☺1✉10❤
FTX☺AFM☺1☺☺TZUN TZU❤
UNS☺S❤
CNT☺2✉4❤
UNT☺22☺SSDD1❤
UNZ☺1☺6002❤

Mapping
-------
>>> edi == make_edi(segments)
True
>>> edi == make_edi(parse_edi(edmoji))
True

XML
---
>>> xml = make_xml(segments)
>>> type(xml)
<class 'xml.etree.ElementTree.Element'>

Indexing
--------
>>> xml[7].tag
'LIN'

Index semantics
---------------
>>> isbns = [elements[2][0].text for elements in xml if elements.tag == 'LIN' and elements[2][1].text == 'IB']
>>> isbns
['0764569104', '0764569090', '1861004656', '0-19-501476-6']

Formatting
----------
>>> ElementTree.tostring(xml)
b"<EDIFACT><UNA>:+.? '</UNA><UNB><UNB0><UNB00>UNOY</UNB00><UNB01>3</UNB01></UNB0><UNB1><UNB10>INVALIDATORSTUDIO</UNB10><UNB11>1</UNB11></UNB1><UNB2><UNB20>BYTESREADER</UNB20><UNB21>1</UNB21></UNB2><UNB3><UNB30>20180630</UNB30><UNB31>1159</UNB31></UNB3><UNB4><UNB40>6002</UNB40></UNB4></UNB><UNH><UNH0><UNH00>SSDD1</UNH00></UNH0><UNH1><UNH10>ORDERS</UNH10><UNH11>D</UNH11><UNH12>03B</UNH12><UNH13>UN</UNH13><UNH14>EAN008</UNH14></UNH1></UNH><BGM><BGM0><BGM00>220</BGM00></BGM0><BGM1><BGM10>BKOD99</BGM10></BGM1><BGM2><BGM20>9</BGM20></BGM2></BGM><DTM><DTM0><DTM00>137</DTM00><DTM01>20180630</DTM01><DTM02>102</DTM02></DTM0></DTM><NAD><NAD0><NAD00>BY</NAD00></NAD0><NAD1><NAD10>31-424-2022</NAD10><NAD11 /><NAD12>16</NAD12></NAD1></NAD><NAD><NAD0><NAD00>SU</NAD00></NAD0><NAD1><NAD10>34-093-1588</NAD10><NAD11 /><NAD12>16</NAD12></NAD1></NAD><LIN><LIN0><LIN00>1</LIN00></LIN0><LIN1><LIN10>1</LIN10></LIN1><LIN2><LIN20>0764569104</LIN20><LIN21>IB</LIN21></LIN2></LIN><QTY><QTY0><QTY00>1</QTY00><QTY01>25</QTY01></QTY0></QTY><FTX><FTX0><FTX00>AFM</FTX00></FTX0><FTX1><FTX10>1</FTX10></FTX1><FTX2><FTX20 /></FTX2><FTX3><FTX30>XPATH 2.0 PROGRAMMER'S REFERENCE</FTX30></FTX3></FTX><LIN><LIN0><LIN00>2</LIN00></LIN0><LIN1><LIN10>1</LIN10></LIN1><LIN2><LIN20>0764569090</LIN20><LIN21>IB</LIN21></LIN2></LIN><QTY><QTY0><QTY00>1</QTY00><QTY01>25</QTY01></QTY0></QTY><FTX><FTX0><FTX00>AFM</FTX00></FTX0><FTX1><FTX10>1</FTX10></FTX1><FTX2><FTX20 /></FTX2><FTX3><FTX30>XSLT 2.0 PROGRAMMER'S REFERENCE</FTX30></FTX3></FTX><LIN><LIN0><LIN00>3</LIN00></LIN0><LIN1><LIN10>1</LIN10></LIN1><LIN2><LIN20>1861004656</LIN20><LIN21>IB</LIN21></LIN2></LIN><QTY><QTY0><QTY00>1</QTY00><QTY01>16</QTY01></QTY0></QTY><FTX><FTX0><FTX00>AFM</FTX00></FTX0><FTX1><FTX10>1</FTX10></FTX1><FTX2><FTX20 /></FTX2><FTX3><FTX30>JAVA SERVER PROGRAMMING</FTX30></FTX3></FTX><LIN><LIN0><LIN00>4</LIN00></LIN0><LIN1><LIN10>1</LIN10></LIN1><LIN2><LIN20>0-19-501476-6</LIN20><LIN21>IB</LIN21></LIN2></LIN><QTY><QTY0><QTY00>1</QTY00><QTY01>10</QTY01></QTY0></QTY><FTX><FTX0><FTX00>AFM</FTX00></FTX0><FTX1><FTX10>1</FTX10></FTX1><FTX2><FTX20 /></FTX2><FTX3><FTX30>TZUN TZU</FTX30></FTX3></FTX><UNS><UNS0><UNS00>S</UNS00></UNS0></UNS><CNT><CNT0><CNT00>2</CNT00><CNT01>4</CNT01></CNT0></CNT><UNT><UNT0><UNT00>22</UNT00></UNT0><UNT1><UNT10>SSDD1</UNT10></UNT1></UNT><UNZ><UNZ0><UNZ00>1</UNZ00></UNZ0><UNZ1><UNZ10>6002</UNZ10></UNZ1></UNZ></EDIFACT>"

>>> print(ElementTree.tostring(xml, encoding='utf8').decode('utf8'))
<?xml version='1.0' encoding='utf8'?>
<EDIFACT><UNA>:+.? '</UNA><UNB><UNB0><UNB00>UNOY</UNB00><UNB01>3</UNB01></UNB0><UNB1><UNB10>INVALIDATORSTUDIO</UNB10><UNB11>1</UNB11></UNB1><UNB2><UNB20>BYTESREADER</UNB20><UNB21>1</UNB21></UNB2><UNB3><UNB30>20180630</UNB30><UNB31>1159</UNB31></UNB3><UNB4><UNB40>6002</UNB40></UNB4></UNB><UNH><UNH0><UNH00>SSDD1</UNH00></UNH0><UNH1><UNH10>ORDERS</UNH10><UNH11>D</UNH11><UNH12>03B</UNH12><UNH13>UN</UNH13><UNH14>EAN008</UNH14></UNH1></UNH><BGM><BGM0><BGM00>220</BGM00></BGM0><BGM1><BGM10>BKOD99</BGM10></BGM1><BGM2><BGM20>9</BGM20></BGM2></BGM><DTM><DTM0><DTM00>137</DTM00><DTM01>20180630</DTM01><DTM02>102</DTM02></DTM0></DTM><NAD><NAD0><NAD00>BY</NAD00></NAD0><NAD1><NAD10>31-424-2022</NAD10><NAD11 /><NAD12>16</NAD12></NAD1></NAD><NAD><NAD0><NAD00>SU</NAD00></NAD0><NAD1><NAD10>34-093-1588</NAD10><NAD11 /><NAD12>16</NAD12></NAD1></NAD><LIN><LIN0><LIN00>1</LIN00></LIN0><LIN1><LIN10>1</LIN10></LIN1><LIN2><LIN20>0764569104</LIN20><LIN21>IB</LIN21></LIN2></LIN><QTY><QTY0><QTY00>1</QTY00><QTY01>25</QTY01></QTY0></QTY><FTX><FTX0><FTX00>AFM</FTX00></FTX0><FTX1><FTX10>1</FTX10></FTX1><FTX2><FTX20 /></FTX2><FTX3><FTX30>XPATH 2.0 PROGRAMMER'S REFERENCE</FTX30></FTX3></FTX><LIN><LIN0><LIN00>2</LIN00></LIN0><LIN1><LIN10>1</LIN10></LIN1><LIN2><LIN20>0764569090</LIN20><LIN21>IB</LIN21></LIN2></LIN><QTY><QTY0><QTY00>1</QTY00><QTY01>25</QTY01></QTY0></QTY><FTX><FTX0><FTX00>AFM</FTX00></FTX0><FTX1><FTX10>1</FTX10></FTX1><FTX2><FTX20 /></FTX2><FTX3><FTX30>XSLT 2.0 PROGRAMMER'S REFERENCE</FTX30></FTX3></FTX><LIN><LIN0><LIN00>3</LIN00></LIN0><LIN1><LIN10>1</LIN10></LIN1><LIN2><LIN20>1861004656</LIN20><LIN21>IB</LIN21></LIN2></LIN><QTY><QTY0><QTY00>1</QTY00><QTY01>16</QTY01></QTY0></QTY><FTX><FTX0><FTX00>AFM</FTX00></FTX0><FTX1><FTX10>1</FTX10></FTX1><FTX2><FTX20 /></FTX2><FTX3><FTX30>JAVA SERVER PROGRAMMING</FTX30></FTX3></FTX><LIN><LIN0><LIN00>4</LIN00></LIN0><LIN1><LIN10>1</LIN10></LIN1><LIN2><LIN20>0-19-501476-6</LIN20><LIN21>IB</LIN21></LIN2></LIN><QTY><QTY0><QTY00>1</QTY00><QTY01>10</QTY01></QTY0></QTY><FTX><FTX0><FTX00>AFM</FTX00></FTX0><FTX1><FTX10>1</FTX10></FTX1><FTX2><FTX20 /></FTX2><FTX3><FTX30>TZUN TZU</FTX30></FTX3></FTX><UNS><UNS0><UNS00>S</UNS00></UNS0></UNS><CNT><CNT0><CNT00>2</CNT00><CNT01>4</CNT01></CNT0></CNT><UNT><UNT0><UNT00>22</UNT00></UNT0><UNT1><UNT10>SSDD1</UNT10></UNT1></UNT><UNZ><UNZ0><UNZ00>1</UNZ00></UNZ0><UNZ1><UNZ10>6002</UNZ10></UNZ1></UNZ></EDIFACT>

>>> print(pretty_xml(xml))
<?xml version="1.0" ?>
<EDIFACT>
    <UNA>:+.? '</UNA>
    <UNB>
        <UNB0>
            <UNB00>UNOY</UNB00>
            <UNB01>3</UNB01>
        </UNB0>
        <UNB1>
            <UNB10>INVALIDATORSTUDIO</UNB10>
            <UNB11>1</UNB11>
        </UNB1>
        <UNB2>
            <UNB20>BYTESREADER</UNB20>
            <UNB21>1</UNB21>
        </UNB2>
        <UNB3>
            <UNB30>20180630</UNB30>
            <UNB31>1159</UNB31>
        </UNB3>
        <UNB4>
            <UNB40>6002</UNB40>
        </UNB4>
    </UNB>
    <UNH>
        <UNH0>
            <UNH00>SSDD1</UNH00>
        </UNH0>
        <UNH1>
            <UNH10>ORDERS</UNH10>
            <UNH11>D</UNH11>
            <UNH12>03B</UNH12>
            <UNH13>UN</UNH13>
            <UNH14>EAN008</UNH14>
        </UNH1>
    </UNH>
    <BGM>
        <BGM0>
            <BGM00>220</BGM00>
        </BGM0>
        <BGM1>
            <BGM10>BKOD99</BGM10>
        </BGM1>
        <BGM2>
            <BGM20>9</BGM20>
        </BGM2>
    </BGM>
    <DTM>
        <DTM0>
            <DTM00>137</DTM00>
            <DTM01>20180630</DTM01>
            <DTM02>102</DTM02>
        </DTM0>
    </DTM>
    <NAD>
        <NAD0>
            <NAD00>BY</NAD00>
        </NAD0>
        <NAD1>
            <NAD10>31-424-2022</NAD10>
            <NAD11/>
            <NAD12>16</NAD12>
        </NAD1>
    </NAD>
    <NAD>
        <NAD0>
            <NAD00>SU</NAD00>
        </NAD0>
        <NAD1>
            <NAD10>34-093-1588</NAD10>
            <NAD11/>
            <NAD12>16</NAD12>
        </NAD1>
    </NAD>
    <LIN>
        <LIN0>
            <LIN00>1</LIN00>
        </LIN0>
        <LIN1>
            <LIN10>1</LIN10>
        </LIN1>
        <LIN2>
            <LIN20>0764569104</LIN20>
            <LIN21>IB</LIN21>
        </LIN2>
    </LIN>
    <QTY>
        <QTY0>
            <QTY00>1</QTY00>
            <QTY01>25</QTY01>
        </QTY0>
    </QTY>
    <FTX>
        <FTX0>
            <FTX00>AFM</FTX00>
        </FTX0>
        <FTX1>
            <FTX10>1</FTX10>
        </FTX1>
        <FTX2>
            <FTX20/>
        </FTX2>
        <FTX3>
            <FTX30>XPATH 2.0 PROGRAMMER'S REFERENCE</FTX30>
        </FTX3>
    </FTX>
    <LIN>
        <LIN0>
            <LIN00>2</LIN00>
        </LIN0>
        <LIN1>
            <LIN10>1</LIN10>
        </LIN1>
        <LIN2>
            <LIN20>0764569090</LIN20>
            <LIN21>IB</LIN21>
        </LIN2>
    </LIN>
    <QTY>
        <QTY0>
            <QTY00>1</QTY00>
            <QTY01>25</QTY01>
        </QTY0>
    </QTY>
    <FTX>
        <FTX0>
            <FTX00>AFM</FTX00>
        </FTX0>
        <FTX1>
            <FTX10>1</FTX10>
        </FTX1>
        <FTX2>
            <FTX20/>
        </FTX2>
        <FTX3>
            <FTX30>XSLT 2.0 PROGRAMMER'S REFERENCE</FTX30>
        </FTX3>
    </FTX>
    <LIN>
        <LIN0>
            <LIN00>3</LIN00>
        </LIN0>
        <LIN1>
            <LIN10>1</LIN10>
        </LIN1>
        <LIN2>
            <LIN20>1861004656</LIN20>
            <LIN21>IB</LIN21>
        </LIN2>
    </LIN>
    <QTY>
        <QTY0>
            <QTY00>1</QTY00>
            <QTY01>16</QTY01>
        </QTY0>
    </QTY>
    <FTX>
        <FTX0>
            <FTX00>AFM</FTX00>
        </FTX0>
        <FTX1>
            <FTX10>1</FTX10>
        </FTX1>
        <FTX2>
            <FTX20/>
        </FTX2>
        <FTX3>
            <FTX30>JAVA SERVER PROGRAMMING</FTX30>
        </FTX3>
    </FTX>
    <LIN>
        <LIN0>
            <LIN00>4</LIN00>
        </LIN0>
        <LIN1>
            <LIN10>1</LIN10>
        </LIN1>
        <LIN2>
            <LIN20>0-19-501476-6</LIN20>
            <LIN21>IB</LIN21>
        </LIN2>
    </LIN>
    <QTY>
        <QTY0>
            <QTY00>1</QTY00>
            <QTY01>10</QTY01>
        </QTY0>
    </QTY>
    <FTX>
        <FTX0>
            <FTX00>AFM</FTX00>
        </FTX0>
        <FTX1>
            <FTX10>1</FTX10>
        </FTX1>
        <FTX2>
            <FTX20/>
        </FTX2>
        <FTX3>
            <FTX30>TZUN TZU</FTX30>
        </FTX3>
    </FTX>
    <UNS>
        <UNS0>
            <UNS00>S</UNS00>
        </UNS0>
    </UNS>
    <CNT>
        <CNT0>
            <CNT00>2</CNT00>
            <CNT01>4</CNT01>
        </CNT0>
    </CNT>
    <UNT>
        <UNT0>
            <UNT00>22</UNT00>
        </UNT0>
        <UNT1>
            <UNT10>SSDD1</UNT10>
        </UNT1>
    </UNT>
    <UNZ>
        <UNZ0>
            <UNZ00>1</UNZ00>
        </UNZ0>
        <UNZ1>
            <UNZ10>6002</UNZ10>
        </UNZ1>
    </UNZ>
</EDIFACT>
<BLANKLINE>

Mapping EDI <-> XML
-------------------
>>> edi == make_edi(parse_xml(xml))
True
>>> edi == make_edi(parse_xml(make_xml(parse_edi(edi))))
True
>>> edi == make_edi(parse_xml(make_xml(parse_edi(edmoji))))
True

Experimental
############
Service-Segments and Service-Elements V4
----------------------------------------
>>> import json
>>> v42_sd = json.loads(open('V42-9735-10_service_segments.json').read())
>>> v42_ed = json.loads(open('V42-9735-10_service_codes.json').read())

Version D18A Segments, Elements and Messages
--------------------------------------------
>>> d18a_sd = json.loads(open('d18a_segments.json').read())
>>> d18a_ed = json.loads(open('d18a_codes.json').read())
>>> d18a_md = json.loads(open('d18a_messages.json').read())

>>> sd = {**v42_sd, **d18a_sd}
>>> ed = {**v42_ed, **d18a_ed}

>>> print(report(segments, sd, ed))
UNB+UNOY:3+INVALIDATORSTUDIO:1+BYTESREADER:1+20180630:1159+6002'
----------------------------------------------------------------
Interchange header <UNB>
  SYNTAX IDENTIFIER (S001)
    Syntax identifier <UNOY> (0001) UN/ECE level Y
    Syntax version number <3> (0002) Version 3
  INTERCHANGE SENDER (S002)
    Interchange sender identification <INVALIDATORSTUDIO> (0004)
    Identification code qualifier <1> (0007) DUNS (Data Universal Numbering System)
  INTERCHANGE RECIPIENT (S003)
    Interchange recipient identification <BYTESREADER> (0010)
    Identification code qualifier <1> (0007) DUNS (Data Universal Numbering System)
  DATE AND TIME OF PREPARATION (S004)
    Date <20180630> (0017)
    Time <1159> (0019)
    Interchange control reference <6002> (0020)
<BLANKLINE>
UNH+SSDD1+ORDERS:D:03B:UN:EAN008'
---------------------------------
MESSAGE HEADER <UNH>
    Message reference number <SSDD1> (0062)
  MESSAGE IDENTIFIER (S009)
    Message type <ORDERS> (0065) Purchase order message
    Message version number <D> (0052) Draft version/UN/EDIFACT Directory
    Message release number <03B> (0054) Release 2003 - B
    Controlling agency, coded <UN> (0051) UN/CEFACT
    Association assigned code <EAN008> (0057) GS1 version control number (GS1 Permanent Code)
<BLANKLINE>
BGM+220+BKOD99+9'
-----------------
BEGINNING OF MESSAGE <BGM>
  DOCUMENT/MESSAGE NAME (C002)
    Document name code <220> (1001) Order
  DOCUMENT/MESSAGE IDENTIFICATION (C106)
    Document identifier <BKOD99> (1004)
    MESSAGE FUNCTION CODE <9> (1225) Original
<BLANKLINE>
DTM+137:20180630:102'
---------------------
DATE/TIME/PERIOD <DTM>
  DATE/TIME/PERIOD (C507)
    Date or time or period function code qualifier <137> (2005) Document issue date time
    Date or time or period text <20180630> (2380)
    Date or time or period format code <102> (2379) CCYYMMDD
<BLANKLINE>
NAD+BY+31-424-2022::16'
-----------------------
NAME AND ADDRESS <NAD>
    PARTY FUNCTION CODE QUALIFIER <BY> (3035) Buyer
  PARTY IDENTIFICATION DETAILS (C082)
    Party identifier <31-424-2022> (3039)
    Code list identification code <> (1131)
    Code list responsible agency code <16> (3055) US, D&B (Dun & Bradstreet Corporation)
<BLANKLINE>
NAD+SU+34-093-1588::16'
-----------------------
NAME AND ADDRESS <NAD>
    PARTY FUNCTION CODE QUALIFIER <SU> (3035) Supplier
  PARTY IDENTIFICATION DETAILS (C082)
    Party identifier <34-093-1588> (3039)
    Code list identification code <> (1131)
    Code list responsible agency code <16> (3055) US, D&B (Dun & Bradstreet Corporation)
<BLANKLINE>
LIN+1+1+0764569104:IB'
----------------------
LINE ITEM <LIN>
    LINE ITEM IDENTIFIER <1> (1082)
    ACTION CODE <1> (1229) Added
  ITEM NUMBER IDENTIFICATION (C212)
    Item identifier <0764569104> (7140)
    Item type identification code <IB> (7143) ISBN (International Standard Book Number)
<BLANKLINE>
QTY+1:25'
---------
QUANTITY <QTY>
  QUANTITY DETAILS (C186)
    Quantity type code qualifier <1> (6063) Discrete quantity
    Quantity <25> (6060)
<BLANKLINE>
FTX+AFM+1++XPATH 2.0 PROGRAMMER?'S REFERENCE'
---------------------------------------------
FREE TEXT <FTX>
    TEXT SUBJECT CODE QUALIFIER <AFM> (4451) Title
    FREE TEXT FUNCTION CODE <1> (4453) Text for subsequent use
  TEXT REFERENCE (C107)
    Free text description code <> (4441)
  TEXT LITERAL (C108)
    Free text <XPATH 2.0 PROGRAMMER'S REFERENCE> (4440)
<BLANKLINE>
LIN+2+1+0764569090:IB'
----------------------
LINE ITEM <LIN>
    LINE ITEM IDENTIFIER <2> (1082)
    ACTION CODE <1> (1229) Added
  ITEM NUMBER IDENTIFICATION (C212)
    Item identifier <0764569090> (7140)
    Item type identification code <IB> (7143) ISBN (International Standard Book Number)
<BLANKLINE>
QTY+1:25'
---------
QUANTITY <QTY>
  QUANTITY DETAILS (C186)
    Quantity type code qualifier <1> (6063) Discrete quantity
    Quantity <25> (6060)
<BLANKLINE>
FTX+AFM+1++XSLT 2.0 PROGRAMMER?'S REFERENCE'
--------------------------------------------
FREE TEXT <FTX>
    TEXT SUBJECT CODE QUALIFIER <AFM> (4451) Title
    FREE TEXT FUNCTION CODE <1> (4453) Text for subsequent use
  TEXT REFERENCE (C107)
    Free text description code <> (4441)
  TEXT LITERAL (C108)
    Free text <XSLT 2.0 PROGRAMMER'S REFERENCE> (4440)
<BLANKLINE>
LIN+3+1+1861004656:IB'
----------------------
LINE ITEM <LIN>
    LINE ITEM IDENTIFIER <3> (1082)
    ACTION CODE <1> (1229) Added
  ITEM NUMBER IDENTIFICATION (C212)
    Item identifier <1861004656> (7140)
    Item type identification code <IB> (7143) ISBN (International Standard Book Number)
<BLANKLINE>
QTY+1:16'
---------
QUANTITY <QTY>
  QUANTITY DETAILS (C186)
    Quantity type code qualifier <1> (6063) Discrete quantity
    Quantity <16> (6060)
<BLANKLINE>
FTX+AFM+1++JAVA SERVER PROGRAMMING'
-----------------------------------
FREE TEXT <FTX>
    TEXT SUBJECT CODE QUALIFIER <AFM> (4451) Title
    FREE TEXT FUNCTION CODE <1> (4453) Text for subsequent use
  TEXT REFERENCE (C107)
    Free text description code <> (4441)
  TEXT LITERAL (C108)
    Free text <JAVA SERVER PROGRAMMING> (4440)
<BLANKLINE>
LIN+4+1+0-19-501476-6:IB'
-------------------------
LINE ITEM <LIN>
    LINE ITEM IDENTIFIER <4> (1082)
    ACTION CODE <1> (1229) Added
  ITEM NUMBER IDENTIFICATION (C212)
    Item identifier <0-19-501476-6> (7140)
    Item type identification code <IB> (7143) ISBN (International Standard Book Number)
<BLANKLINE>
QTY+1:10'
---------
QUANTITY <QTY>
  QUANTITY DETAILS (C186)
    Quantity type code qualifier <1> (6063) Discrete quantity
    Quantity <10> (6060)
<BLANKLINE>
FTX+AFM+1++TZUN TZU'
--------------------
FREE TEXT <FTX>
    TEXT SUBJECT CODE QUALIFIER <AFM> (4451) Title
    FREE TEXT FUNCTION CODE <1> (4453) Text for subsequent use
  TEXT REFERENCE (C107)
    Free text description code <> (4441)
  TEXT LITERAL (C108)
    Free text <TZUN TZU> (4440)
<BLANKLINE>
UNS+S'
------
SECTION CONTROL <UNS>
    Section identification <S> (0081) Detail/summary section separation
<BLANKLINE>
CNT+2:4'
--------
CONTROL TOTAL <CNT>
  CONTROL (C270)
    Control total type code qualifier <2> (6069) Number of line items in message
    Control total quantity <4> (6066)
<BLANKLINE>
UNT+22+SSDD1'
-------------
MESSAGE TRAILER <UNT>
    Number of segments in a message <22> (0074)
    Message reference number <SSDD1> (0062)
<BLANKLINE>
UNZ+1+6002'
-----------
Section control <UNZ>
    Interchange control count <1> (0036)
    Interchange control reference <6002> (0020)
<BLANKLINE>

>>> edi_xml = make_edi_xml(segments, sd, ed)
>>> print(pretty_xml(edi_xml))
<?xml version="1.0" ?>
<EDIFACT>
    <UNA>:+.? '</UNA>
    <UNB description="Function: To identify an interchange" name="Interchange header">
        <UNB0 code="S001" mc="M" name="SYNTAX IDENTIFIER" pos="10" repeat="1">
            <UNB00 code="0001" description="ISO 10646-1 octet without code extension technique." mc="M" name="Syntax identifier" representation="a4" value="UN/ECE level Y">UNOY</UNB00>
            <UNB01 code="0002" description="ISO 9735 Amendment 1:1992." mc="M" name="Syntax version number" representation="an1" value="Version 3">3</UNB01>
        </UNB0>
        <UNB1 code="S002" mc="M" name="INTERCHANGE SENDER" pos="20" repeat="1">
            <UNB10 code="0004" mc="M" name="Interchange sender identification" representation="an..35">INVALIDATORSTUDIO</UNB10>
            <UNB11 code="0007" description="Partner identification code assigned by Dun &amp; Bradstreet." mc="C" name="Identification code qualifier" representation="an..4" value="DUNS (Data Universal Numbering System)">1</UNB11>
        </UNB1>
        <UNB2 code="S003" mc="M" name="INTERCHANGE RECIPIENT" pos="30" repeat="1">
            <UNB20 code="0010" mc="M" name="Interchange recipient identification" representation="an..35">BYTESREADER</UNB20>
            <UNB21 code="0007" description="Partner identification code assigned by Dun &amp; Bradstreet." mc="C" name="Identification code qualifier" representation="an..4" value="DUNS (Data Universal Numbering System)">1</UNB21>
        </UNB2>
        <UNB3 code="S004" mc="M" name="DATE AND TIME OF PREPARATION" pos="40" repeat="1">
            <UNB30 code="0017" mc="M" name="Date" representation="n8">20180630</UNB30>
            <UNB31 code="0019" mc="M" name="Time" representation="n4">1159</UNB31>
        </UNB3>
        <UNB4 mc="M" pos="50" repeat="1">
            <UNB40 code="0020" mc="M" name="Interchange control reference" representation="an..14">6002</UNB40>
        </UNB4>
    </UNB>
    <UNH description="To head, identify and specify a message. Notes: 1. Data element S009/0057 is retained for upward compatibility. The use of S016 and/or S017 is encouraged in preference. 2. The combination of the values carried in data elements 0062 and S009 shall be used to identify uniquely the message within its group (if used) or if not used, within its interchange, for the purpose of acknowledgement." name="MESSAGE HEADER">
        <UNH0 mc="M" pos="10" repeat="1">
            <UNH00 code="0062" mc="M" name="Message reference number" representation="an..14">SSDD1</UNH00>
        </UNH0>
        <UNH1 code="S009" mc="M" name="MESSAGE IDENTIFIER" pos="20" repeat="1">
            <UNH10 code="0065" description="A code to identify the purchase order message." mc="M" name="Message type" representation="an..6" value="Purchase order message">ORDERS</UNH10>
            <UNH11 code="0052" description="Message approved and issued as a draft message (Valid for directories published after March 1993 and prior to March 1997). Message approved as a standard message (Valid for directories published after March 1997)." mc="M" name="Message version number" representation="an..3" value="Draft version/UN/EDIFACT Directory">D</UNH11>
            <UNH12 code="0054" description="Message approved and issued in the second 2003 release of the UNTDID (United Nations Trade Data Interchange Directory)." mc="M" name="Message release number" representation="an..3" value="Release 2003 - B">03B</UNH12>
            <UNH13 code="0051" description="United Nations Centre for Trade Facilitation and Electronic Business (UN/CEFACT)." mc="M" name="Controlling agency, coded" representation="an..3" value="UN/CEFACT">UN</UNH13>
            <UNH14 code="0057" description="GS1 version control number (GS1 Permanent Code)" mc="C" name="Association assigned code" representation="an..6" value="GS1 version control number (GS1 Permanent Code)">EAN008</UNH14>
        </UNH1>
    </UNH>
    <BGM description="Function: To indicate the type and function of a message and to transmit the identifying number." name="BEGINNING OF MESSAGE">
        <BGM0 code="C002" mc="C" name="DOCUMENT/MESSAGE NAME" pos="10" repeat="1">
            <BGM00 code="1001" description="Document/message by means of which a buyer initiates a transaction with a seller involving the supply of goods or services as specified, according to conditions set out in an offer, or otherwise known to the buyer." mc="C" name="Document name code" representation="an..3" value="Order">220</BGM00>
        </BGM0>
        <BGM1 code="C106" mc="C" name="DOCUMENT/MESSAGE IDENTIFICATION" pos="20" repeat="1">
            <BGM10 code="1004" mc="C" name="Document identifier" representation="an..70">BKOD99</BGM10>
        </BGM1>
        <BGM2 mc="C" pos="30" repeat="1">
            <BGM20 code="1225" description="Initial transmission related to a given transaction." mc="C" name="MESSAGE FUNCTION CODE" representation="an..3" value="Original">9</BGM20>
        </BGM2>
    </BGM>
    <DTM description="Function: To specify date, and/or time, or period." name="DATE/TIME/PERIOD">
        <DTM0 code="C507" mc="M" name="DATE/TIME/PERIOD" pos="10" repeat="1">
            <DTM00 code="2005" description="[2007] Date that a document was issued and when appropriate, signed or otherwise authenticated." mc="M" name="Date or time or period function code qualifier" representation="an..3" value="Document issue date time">137</DTM00>
            <DTM01 code="2380" mc="C" name="Date or time or period text" representation="an..35">20180630</DTM01>
            <DTM02 code="2379" description="Calendar date: C = Century ; Y = Year ; M = Month ; D = Day." mc="C" name="Date or time or period format code" representation="an..3" value="CCYYMMDD">102</DTM02>
        </DTM0>
    </DTM>
    <NAD description="Function: To specify the name/address and their related function, either by C082 only and/or unstructured by C058 or structured by C080 thru 3207." name="NAME AND ADDRESS">
        <NAD0 mc="M" pos="10" repeat="1">
            <NAD00 code="3035" description="[3002] Party to which merchandise or services are sold." mc="M" name="PARTY FUNCTION CODE QUALIFIER" representation="an..3" value="Buyer">BY</NAD00>
        </NAD0>
        <NAD1 code="C082" mc="C" name="PARTY IDENTIFICATION DETAILS" pos="20" repeat="1">
            <NAD10 code="3039" mc="M" name="Party identifier" representation="an..35">31-424-2022</NAD10>
            <NAD11 code="1131" mc="C" name="Code list identification code" representation="an..17"/>
            <NAD12 code="3055" description="Identifies the Dun &amp; Bradstreet Corporation, United States." mc="C" name="Code list responsible agency code" representation="an..3" value="US, D&amp;B (Dun &amp; Bradstreet Corporation)">16</NAD12>
        </NAD1>
    </NAD>
    <NAD description="Function: To specify the name/address and their related function, either by C082 only and/or unstructured by C058 or structured by C080 thru 3207." name="NAME AND ADDRESS">
        <NAD0 mc="M" pos="10" repeat="1">
            <NAD00 code="3035" description="Party who supplies goods and or services." mc="M" name="PARTY FUNCTION CODE QUALIFIER" representation="an..3" value="Supplier">SU</NAD00>
        </NAD0>
        <NAD1 code="C082" mc="C" name="PARTY IDENTIFICATION DETAILS" pos="20" repeat="1">
            <NAD10 code="3039" mc="M" name="Party identifier" representation="an..35">34-093-1588</NAD10>
            <NAD11 code="1131" mc="C" name="Code list identification code" representation="an..17"/>
            <NAD12 code="3055" description="Identifies the Dun &amp; Bradstreet Corporation, United States." mc="C" name="Code list responsible agency code" representation="an..3" value="US, D&amp;B (Dun &amp; Bradstreet Corporation)">16</NAD12>
        </NAD1>
    </NAD>
    <LIN description="Function: To identify a line item and configuration." name="LINE ITEM">
        <LIN0 mc="C" pos="10" repeat="1">
            <LIN00 code="1082" mc="C" name="LINE ITEM IDENTIFIER" representation="an..6">1</LIN00>
        </LIN0>
        <LIN1 mc="C" pos="20" repeat="1">
            <LIN10 code="1229" description="The information is to be or has been added." mc="C" name="ACTION CODE" representation="an..3" value="Added">1</LIN10>
        </LIN1>
        <LIN2 code="C212" mc="C" name="ITEM NUMBER IDENTIFICATION" pos="30" repeat="1">
            <LIN20 code="7140" mc="C" name="Item identifier" representation="an..35">0764569104</LIN20>
            <LIN21 code="7143" description="A unique number identifying a book." mc="C" name="Item type identification code" representation="an..3" value="ISBN (International Standard Book Number)">IB</LIN21>
        </LIN2>
    </LIN>
    <QTY description="Function: To specify a pertinent quantity." name="QUANTITY">
        <QTY0 code="C186" mc="M" name="QUANTITY DETAILS" pos="10" repeat="1">
            <QTY00 code="6063" description="Individually separated and distinct quantity." mc="M" name="Quantity type code qualifier" representation="an..3" value="Discrete quantity">1</QTY00>
            <QTY01 code="6060" mc="M" name="Quantity" representation="an..35">25</QTY01>
        </QTY0>
    </QTY>
    <FTX description="Function: To provide free form or coded text information." name="FREE TEXT">
        <FTX0 mc="M" pos="10" repeat="1">
            <FTX00 code="4451" description="Denotes that the associated text is a title." mc="M" name="TEXT SUBJECT CODE QUALIFIER" representation="an..3" value="Title">AFM</FTX00>
        </FTX0>
        <FTX1 mc="C" pos="20" repeat="1">
            <FTX10 code="4453" description="The occurrence of this text does not affect message processing." mc="C" name="FREE TEXT FUNCTION CODE" representation="an..3" value="Text for subsequent use">1</FTX10>
        </FTX1>
        <FTX2 code="C107" mc="C" name="TEXT REFERENCE" pos="30" repeat="1">
            <FTX20 code="4441" mc="M" name="Free text description code" representation="an..17"/>
        </FTX2>
        <FTX3 code="C108" mc="C" name="TEXT LITERAL" pos="40" repeat="1">
            <FTX30 code="4440" mc="M" name="Free text" representation="an..512">XPATH 2.0 PROGRAMMER'S REFERENCE</FTX30>
        </FTX3>
    </FTX>
    <LIN description="Function: To identify a line item and configuration." name="LINE ITEM">
        <LIN0 mc="C" pos="10" repeat="1">
            <LIN00 code="1082" mc="C" name="LINE ITEM IDENTIFIER" representation="an..6">2</LIN00>
        </LIN0>
        <LIN1 mc="C" pos="20" repeat="1">
            <LIN10 code="1229" description="The information is to be or has been added." mc="C" name="ACTION CODE" representation="an..3" value="Added">1</LIN10>
        </LIN1>
        <LIN2 code="C212" mc="C" name="ITEM NUMBER IDENTIFICATION" pos="30" repeat="1">
            <LIN20 code="7140" mc="C" name="Item identifier" representation="an..35">0764569090</LIN20>
            <LIN21 code="7143" description="A unique number identifying a book." mc="C" name="Item type identification code" representation="an..3" value="ISBN (International Standard Book Number)">IB</LIN21>
        </LIN2>
    </LIN>
    <QTY description="Function: To specify a pertinent quantity." name="QUANTITY">
        <QTY0 code="C186" mc="M" name="QUANTITY DETAILS" pos="10" repeat="1">
            <QTY00 code="6063" description="Individually separated and distinct quantity." mc="M" name="Quantity type code qualifier" representation="an..3" value="Discrete quantity">1</QTY00>
            <QTY01 code="6060" mc="M" name="Quantity" representation="an..35">25</QTY01>
        </QTY0>
    </QTY>
    <FTX description="Function: To provide free form or coded text information." name="FREE TEXT">
        <FTX0 mc="M" pos="10" repeat="1">
            <FTX00 code="4451" description="Denotes that the associated text is a title." mc="M" name="TEXT SUBJECT CODE QUALIFIER" representation="an..3" value="Title">AFM</FTX00>
        </FTX0>
        <FTX1 mc="C" pos="20" repeat="1">
            <FTX10 code="4453" description="The occurrence of this text does not affect message processing." mc="C" name="FREE TEXT FUNCTION CODE" representation="an..3" value="Text for subsequent use">1</FTX10>
        </FTX1>
        <FTX2 code="C107" mc="C" name="TEXT REFERENCE" pos="30" repeat="1">
            <FTX20 code="4441" mc="M" name="Free text description code" representation="an..17"/>
        </FTX2>
        <FTX3 code="C108" mc="C" name="TEXT LITERAL" pos="40" repeat="1">
            <FTX30 code="4440" mc="M" name="Free text" representation="an..512">XSLT 2.0 PROGRAMMER'S REFERENCE</FTX30>
        </FTX3>
    </FTX>
    <LIN description="Function: To identify a line item and configuration." name="LINE ITEM">
        <LIN0 mc="C" pos="10" repeat="1">
            <LIN00 code="1082" mc="C" name="LINE ITEM IDENTIFIER" representation="an..6">3</LIN00>
        </LIN0>
        <LIN1 mc="C" pos="20" repeat="1">
            <LIN10 code="1229" description="The information is to be or has been added." mc="C" name="ACTION CODE" representation="an..3" value="Added">1</LIN10>
        </LIN1>
        <LIN2 code="C212" mc="C" name="ITEM NUMBER IDENTIFICATION" pos="30" repeat="1">
            <LIN20 code="7140" mc="C" name="Item identifier" representation="an..35">1861004656</LIN20>
            <LIN21 code="7143" description="A unique number identifying a book." mc="C" name="Item type identification code" representation="an..3" value="ISBN (International Standard Book Number)">IB</LIN21>
        </LIN2>
    </LIN>
    <QTY description="Function: To specify a pertinent quantity." name="QUANTITY">
        <QTY0 code="C186" mc="M" name="QUANTITY DETAILS" pos="10" repeat="1">
            <QTY00 code="6063" description="Individually separated and distinct quantity." mc="M" name="Quantity type code qualifier" representation="an..3" value="Discrete quantity">1</QTY00>
            <QTY01 code="6060" mc="M" name="Quantity" representation="an..35">16</QTY01>
        </QTY0>
    </QTY>
    <FTX description="Function: To provide free form or coded text information." name="FREE TEXT">
        <FTX0 mc="M" pos="10" repeat="1">
            <FTX00 code="4451" description="Denotes that the associated text is a title." mc="M" name="TEXT SUBJECT CODE QUALIFIER" representation="an..3" value="Title">AFM</FTX00>
        </FTX0>
        <FTX1 mc="C" pos="20" repeat="1">
            <FTX10 code="4453" description="The occurrence of this text does not affect message processing." mc="C" name="FREE TEXT FUNCTION CODE" representation="an..3" value="Text for subsequent use">1</FTX10>
        </FTX1>
        <FTX2 code="C107" mc="C" name="TEXT REFERENCE" pos="30" repeat="1">
            <FTX20 code="4441" mc="M" name="Free text description code" representation="an..17"/>
        </FTX2>
        <FTX3 code="C108" mc="C" name="TEXT LITERAL" pos="40" repeat="1">
            <FTX30 code="4440" mc="M" name="Free text" representation="an..512">JAVA SERVER PROGRAMMING</FTX30>
        </FTX3>
    </FTX>
    <LIN description="Function: To identify a line item and configuration." name="LINE ITEM">
        <LIN0 mc="C" pos="10" repeat="1">
            <LIN00 code="1082" mc="C" name="LINE ITEM IDENTIFIER" representation="an..6">4</LIN00>
        </LIN0>
        <LIN1 mc="C" pos="20" repeat="1">
            <LIN10 code="1229" description="The information is to be or has been added." mc="C" name="ACTION CODE" representation="an..3" value="Added">1</LIN10>
        </LIN1>
        <LIN2 code="C212" mc="C" name="ITEM NUMBER IDENTIFICATION" pos="30" repeat="1">
            <LIN20 code="7140" mc="C" name="Item identifier" representation="an..35">0-19-501476-6</LIN20>
            <LIN21 code="7143" description="A unique number identifying a book." mc="C" name="Item type identification code" representation="an..3" value="ISBN (International Standard Book Number)">IB</LIN21>
        </LIN2>
    </LIN>
    <QTY description="Function: To specify a pertinent quantity." name="QUANTITY">
        <QTY0 code="C186" mc="M" name="QUANTITY DETAILS" pos="10" repeat="1">
            <QTY00 code="6063" description="Individually separated and distinct quantity." mc="M" name="Quantity type code qualifier" representation="an..3" value="Discrete quantity">1</QTY00>
            <QTY01 code="6060" mc="M" name="Quantity" representation="an..35">10</QTY01>
        </QTY0>
    </QTY>
    <FTX description="Function: To provide free form or coded text information." name="FREE TEXT">
        <FTX0 mc="M" pos="10" repeat="1">
            <FTX00 code="4451" description="Denotes that the associated text is a title." mc="M" name="TEXT SUBJECT CODE QUALIFIER" representation="an..3" value="Title">AFM</FTX00>
        </FTX0>
        <FTX1 mc="C" pos="20" repeat="1">
            <FTX10 code="4453" description="The occurrence of this text does not affect message processing." mc="C" name="FREE TEXT FUNCTION CODE" representation="an..3" value="Text for subsequent use">1</FTX10>
        </FTX1>
        <FTX2 code="C107" mc="C" name="TEXT REFERENCE" pos="30" repeat="1">
            <FTX20 code="4441" mc="M" name="Free text description code" representation="an..17"/>
        </FTX2>
        <FTX3 code="C108" mc="C" name="TEXT LITERAL" pos="40" repeat="1">
            <FTX30 code="4440" mc="M" name="Free text" representation="an..512">TZUN TZU</FTX30>
        </FTX3>
    </FTX>
    <UNS description="To separate header, detail and summary sections of a message. Notes: To be used by message designers only when required to avoid ambiguities." name="SECTION CONTROL">
        <UNS0 mc="M" pos="10" repeat="1">
            <UNS00 code="0081" description="To qualify the segment UNS, when separating the detail from the summary section of a message." mc="M" name="Section identification" representation="a1" value="Detail/summary section separation">S</UNS00>
        </UNS0>
    </UNS>
    <CNT description="Function: To provide control total." name="CONTROL TOTAL">
        <CNT0 code="C270" mc="M" name="CONTROL" pos="10" repeat="1">
            <CNT00 code="6069" description="Total number of line items in the message." mc="M" name="Control total type code qualifier" representation="an..3" value="Number of line items in message">2</CNT00>
            <CNT01 code="6066" mc="M" name="Control total quantity" representation="n..18">4</CNT01>
        </CNT0>
    </CNT>
    <UNT description="To end and check the completeness of a message. Notes: 1. 0062, the value shall be identical to the value in 0062 in the corresponding UNH segment." name="MESSAGE TRAILER">
        <UNT0 mc="M" pos="10" repeat="1">
            <UNT00 code="0074" mc="M" name="Number of segments in a message" representation="n..10">22</UNT00>
        </UNT0>
        <UNT1 mc="M" pos="20" repeat="1">
            <UNT10 code="0062" mc="M" name="Message reference number" representation="an..14">SSDD1</UNT10>
        </UNT1>
    </UNT>
    <UNZ description="Function: To separate header, detail and summary sections of a message. Note: To be used by message designers only when required to avoid ambiguities." name="Section control">
        <UNZ0 mc="M" pos="10" repeat="1">
            <UNZ00 code="0036" mc="M" name="Interchange control count" representation="n..6">1</UNZ00>
        </UNZ0>
        <UNZ1 mc="M" pos="20" repeat="1">
            <UNZ10 code="0020" mc="M" name="Interchange control reference" representation="an..14">6002</UNZ10>
        </UNZ1>
    </UNZ>
</EDIFACT>
<BLANKLINE>

"""
import re
import pprint
import xml.dom.minidom
import xml.etree.ElementTree
from xml.etree import ElementTree


# EDIFACT special-characters defined by UNA:+.? '
COMPONENT_SEPARATOR = ':'    # delimiter between 'components'
DATAELEMENT_SEPARATOR = '+'  # delimiter between 'data-elements'
DECIMAL_MARK = '.'           # decimal-point-character for 'numeric values'
RELEASE_CHAR = '?'           # escape-char
SPACE = ' '                  # space (fix)
SEGMENT_TERMINATOR = "'"     # end of a 'segment'

NEWLINE = '\n'
CARRIAGE_RETURN = '\r'

ENCODINGS = {
    'UNOA': {
        'ENCODING': 'ascii',
        'ACCEPTED_CHARACTERS': [
            ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
            'U', 'V', 'W', 'X', 'Y', 'Z',
            '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~'
        ]},
    'UNOB': {
        'ENCODING': 'ascii',
        'ACCEPTED_CHARACTERS': [
            ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
            'U', 'V', 'W', 'X', 'Y', 'Z',
            '[', '\\', ']', '^', '_', '`',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z',
            '{', '|', '}', '~'
        ]},
    'UNOC': {'ENCODING': 'iso8859-1'},       # latin1
    'UNOD': {'ENCODING': 'iso8859-2'},
    'UNOE': {'ENCODING': 'iso8859-5'},
    'UNOF': {'ENCODING': 'iso8859-7'},
    'UNOG': {'ENCODING': 'iso8859-3'},
    'UNOH': {'ENCODING': 'iso8859-4'},
    'UNOI': {'ENCODING': 'iso8859-6'},
    'UNOJ': {'ENCODING': 'iso8859-8'},       # hebrew
    'UNOK': {'ENCODING': 'iso8859-9'},
    'UNOL': {'ENCODING': 'iso8859-15'},
    'UNOX': {'ENCODING': 'iso2022_jp_ext'},  # japan
    'UNOY': {'ENCODING': 'utf8'},            # ISO 10646-1
    'UNOW': {'ENCODING': 'utf16'}            # ISO 10646-1 octet with code extension
}

SEGMENTS = {
    'ADR', 'AGR', 'AJT', 'ALC', 'ALI', 'APP', 'APR', 'ARD', 'ARR', 'ASI', 'ATT', 'AUT', 'BAS', 'BGM', 'BII', 'BUS',
    'CAV', 'CCD', 'CCI', 'CDI', 'CDS', 'CDV', 'CED', 'CIN', 'CLA', 'CLI', 'CMP', 'CNI', 'CNT', 'COD', 'COM', 'COT',
    'CPI', 'CPS', 'CPT', 'CST', 'CTA', 'CUX', 'DAM', 'DFN', 'DGS', 'DII', 'DIM', 'DLI', 'DLM', 'DMS', 'DOC', 'DRD',
    'DSG', 'DSI', 'DTM', 'EDT', 'EFI', 'ELM', 'ELU', 'ELV', 'EMP', 'EQA', 'EQD', 'EQN', 'ERC', 'ERP', 'EVE', 'FCA',
    'FII', 'FNS', 'FNT', 'FOR', 'FSQ', 'FTX', 'GDS', 'GEI', 'GID', 'GIN', 'GIR', 'GOR', 'GPO', 'GRU', 'HAN', 'HYN',
    'ICD', 'IDE', 'IFD', 'IHC', 'IMD', 'IND', 'INP', 'INV', 'IRQ', 'LAN', 'LIN', 'LOC', 'MEA', 'MEM', 'MKS', 'MOA',
    'MSG', 'MTD', 'NAD', 'NAT', 'PAC', 'PAI', 'PAS', 'PCC', 'PCD', 'PCI', 'PDI', 'PER', 'PGI', 'PIA', 'PNA', 'POC',
    'PRC', 'PRI', 'PRV', 'PSD', 'PTY', 'PYT', 'QRS', 'QTY', 'QUA', 'QVR', 'RCS', 'REL', 'RFF', 'RJL', 'RNG', 'ROD',
    'RSL', 'RTE', 'SAL', 'SCC', 'SCD', 'SEG', 'SEL', 'SEQ', 'SFI', 'SGP', 'SGU', 'SPR', 'SPS', 'STA', 'STC', 'STG',
    'STS', 'TAX', 'TCC', 'TDT', 'TEM', 'TMD', 'TMP', 'TOD', 'TPL', 'TRU', 'TSR', 'UCD', 'UCF', 'UCI', 'UCM', 'UCS',
    'UGH', 'UGT', 'UIB', 'UIH', 'UIR', 'UIT', 'UIZ', 'UNB', 'UNE', 'UNG', 'UNH', 'UNO', 'UNP', 'UNS', 'UNT', 'UNZ',
    'USA', 'USB', 'USC', 'USD', 'USE', 'USF', 'USH', 'USL', 'USR', 'UST', 'USU', 'USX', 'USY', 'VLI'
}


def parse_edi(data: bytes,
              component_separator=COMPONENT_SEPARATOR,
              dataelement_separator=DATAELEMENT_SEPARATOR,
              decimal_mark=DECIMAL_MARK,
              release_char=RELEASE_CHAR,
              segment_terminator=SEGMENT_TERMINATOR,
              newline=NEWLINE,
              carriage_return=CARRIAGE_RETURN,
              warn_invalid_characters=False,
              default_encoding='UNOY') -> list:

    assert type(data) == bytes, f'Expected <bytes>, got {type(data).__qualname__}'

    # sniffing the (optional) encoding
    try:
        unb_index = data.index(b'UNB')
    except ValueError:
        unb_index = False
    if unb_index:
        uno_offset = data[unb_index:].index(b'UNO')
        uno = data[unb_index + uno_offset:unb_index + uno_offset+4].decode('ascii')
    else:
        uno = default_encoding
    if uno not in ENCODINGS:
        raise ValueError(f'Unknown encoding {uno}')

    # decode (if default fails, all other encodings are tried)
    try:
        content = data.decode(ENCODINGS[uno]['ENCODING'])
    except UnicodeDecodeError:
        for encoding in ENCODINGS:
            if encoding == uno:
                continue
            try:
                content = data.decode(ENCODINGS[encoding]['ENCODING'])
                break
            except UnicodeDecodeError:
                pass
        else:
            raise UnicodeError(f'This data is unreadable with ANY VALID encoding.')

    # optional, checking the encoded content according to the uno
    if warn_invalid_characters:
        metas = {
            '\r': '\\r - Carriage return',
            '\n': '\\n - Newline',
            '\t': '\\t - Tab'
        }
        for i, c in enumerate(content):
            if not c.isprintable() or ('ACCEPTED_CHARACTERS' in ENCODINGS[uno] and c not in ENCODINGS[uno]['ACCEPTED_CHARACTERS']):
                print(f'Warning {uno} invalid character at index {i} {c if c not in metas else metas[c]}')

    # special-characters defined by optional UNA segment
    if content.startswith('UNA'):
        component_separator, dataelement_separator, decimal_mark, release_char, _, segment_terminator = content[3:9]

    # special-characters must be unique
    chars = [component_separator, dataelement_separator, decimal_mark, release_char, segment_terminator, newline, carriage_return]
    assert len(chars) == len(set(chars)), f'Delimiters must be unique. Got {chars}'

    # handling special-characters as non-regex-metacharacters for pattern matching
    rc = re.escape(release_char)
    st = re.escape(segment_terminator)
    cr = re.escape(carriage_return)
    nl = re.escape(newline)
    ds = re.escape(dataelement_separator)
    cs = re.escape(component_separator)

    # (?<!...) is a negative look-behind for escaped special characters used as values
    pattern_1 = f'(?<!{rc}){st}{cr}?{nl}'
    pattern_2 = f'(?<!{rc}){st}'
    pattern_3 = f'(?<!{rc}){ds}'
    pattern_4 = f'(?<!{rc}){cs}'

    # splitting content on special-characters
    lines = [line.replace(release_char + segment_terminator, segment_terminator)
             for line in re.split(pattern_2, re.sub(pattern_1, segment_terminator, content))][:-1]  # last seg empty

    # parsing the segments
    segments = []
    for i, line in enumerate(lines):
        if line.startswith('UNA'):
            assert i == 0, 'Error: multiple UNA in one message'
            edi_chars = [component_separator, dataelement_separator, decimal_mark, release_char, SPACE, segment_terminator]
            segments.append(['UNA', edi_chars])
            continue

        if line[3] != dataelement_separator:
            raise SyntaxError(f'Segment {i+1}: Expected datalement-separator {dataelement_separator} got {line[3]}')

        segment, data_elements = line[:3], line[4:]
        if segment not in SEGMENTS:
            raise SyntaxError(f'Unknown segment {segment}')
        segments.append([segment, []])
        data_elements = [element.replace(release_char + dataelement_separator, dataelement_separator)
                         for element in re.split(pattern_3, data_elements)]

        for data_element in data_elements:
            components = [component.replace(release_char + component_separator, component_separator)
                          for component in re.split(pattern_4, data_element)]
            segments[len(segments) - 1][1].append(components)

    return segments


def make_edi(segments: list,
             component_separator=COMPONENT_SEPARATOR,
             dataelement_separator=DATAELEMENT_SEPARATOR,
             decimal_mark=DECIMAL_MARK,
             release_char=RELEASE_CHAR,
             segment_terminator=SEGMENT_TERMINATOR,
             newline=NEWLINE,
             carriage_return=CARRIAGE_RETURN,
             default_encoding='UNOY',
             with_newline=False,
             with_carriage_return=False,
             with_una=True) -> bytes:

    # special-characters must be unique
    chars = [component_separator, dataelement_separator, decimal_mark, release_char, segment_terminator, newline, carriage_return]
    assert len(chars) == len(set(chars)), f'Must be unique. Got {chars}'

    strings = []
    if with_una:
        una = component_separator + dataelement_separator + decimal_mark + release_char + SPACE + segment_terminator
        strings.append('UNA' + una)
        if with_carriage_return:
            strings.append(carriage_return)
        if with_newline:
            strings.append(newline)

    for s_i, (segment, data_elements) in enumerate(segments):
        if segment == 'UNA':
            assert s_i == 0, 'Error: multiple UNA in one message'
            continue
        if segment not in SEGMENTS:
            raise SyntaxError(f'Unknown segment {segment}')
        strings.append(segment + dataelement_separator)
        for c_i, components in enumerate(data_elements):
            strings.append(component_separator.join(
                [c.replace(dataelement_separator, release_char + dataelement_separator)
                  .replace(component_separator, release_char + component_separator)
                  .replace(segment_terminator, release_char + segment_terminator)
                 for c in components]))
            if len(data_elements) - 1 != c_i:
                strings.append(dataelement_separator)
        strings.append(segment_terminator)
        if len(segments)-1 != s_i:
            if with_carriage_return:
                strings.append(carriage_return)
            if with_newline:
                strings.append(newline)

    for segment, dataelement in segments:
        if segment == 'UNB':
            uno = dataelement[0][0]
            break
    else:
        uno = default_encoding

    data = ''.join(strings).encode(ENCODINGS[uno]['ENCODING'])
    return data


def make_xml(segments: list, root_tag='EDIFACT') -> ElementTree.Element:
    root = ElementTree.Element(root_tag)

    for s_i, (segment, data_elements) in enumerate(segments):
        if segment == 'UNA':
            assert s_i == 0, 'Error: Multiple UNA in one message'
            ElementTree.SubElement(root, 'UNA').text = ''.join(data_elements)
            continue
        seg_element = ElementTree.SubElement(root, segment)
        for d_i, data_element in enumerate(data_elements):
            data_element_tag = '%s%s' % (segment, d_i)
            data_sub_element = ElementTree.SubElement(seg_element, data_element_tag)
            for c_i, component in enumerate(data_element):
                component_tag = '%s%s%s' % (segment, d_i, c_i)
                component_sub_element = ElementTree.SubElement(data_sub_element, component_tag)
                if component:
                    component_sub_element.text = component

    return root


def parse_xml(root: ElementTree.Element) -> list:
    segments = []

    for e_i, element in enumerate(root):
        if element.tag == 'UNA':
            assert e_i == 0, 'Error: multiple UNA in one message'
            segments.append(['UNA', [c for c in element.text]])
            continue
        segments.append([element.tag])
        values = []
        for d_i, data_element in enumerate(element):
            values.append([])
            for c_i, component in enumerate(data_element):
                if component.text:
                    values[d_i].append(component.text)
                else:
                    values[d_i].append('')
        segments[e_i].append(values)

    return segments


def pretty_xml(root: ElementTree.Element, encoding=None, indent='    ') -> str:
    dom = xml.dom.minidom.parseString(ElementTree.tostring(root).decode())
    return dom.toprettyxml(encoding=encoding, indent=indent)


def report(segments: list, sd: dict, ed: dict) -> str:
    lines = []
    for s_i, (segment, data_elements) in enumerate(segments):
        if segment not in sd:
            if segment != 'UNA':
                lines.append(f'ERROR: skipping undefined segment: <{segment}> at index {s_i}')
            continue
        table = sd[segment]['table']
        edi_line = make_edi([segments[s_i]], with_una=False).decode('utf8')  # todo?
        lines.append(edi_line)
        lines.append('-' * len(edi_line))
        segment_name = f"{sd[segment]['name']} <{segment}>"
        lines.append(segment_name)
        for i_d, data_element in enumerate(data_elements):
            pos = str((i_d+1)*10)
            # different versions, different pos formats '010' '0010'!!!
            cd = [r for r in table if r['pos'] and r['pos'].endswith(pos)][0]
            start = table.index(cd)
            if cd['representation'] is None:
                start += 1
                name = cd['name']
                code = cd['code']
                msg = f'  {name} ({code})'
                lines.append(msg)
            for i_r, r in enumerate(table[start:]):
                if len(data_element) == i_r:
                    break
                code = r['code']
                component = data_element[i_r]
                name = r['name']
                msg = f"    {name} <{component}> ({code})"
                code_name = None
                if component and 'table' in ed[code]:  # todo empty components?
                    if component not in ed[code]['table']:
                        err_msg = f"    ERROR: unknown code <{component}> not in ({code})"
                        lines.append(err_msg)
                    else:
                        code_name = ed[code]['table'][component]['name']
                if code_name:
                    lines.append(msg + ' ' + code_name)
                else:
                    lines.append(msg)
                if component:
                    representation = r['representation']
                    repr_errors = []
                    if '..' in representation:
                        t, d, = representation.split('..')
                    else:
                        d = re.sub('\D', '', representation)
                        t = representation[:representation.index(d)]
                    assert t in ['a', 'n', 'an'], f'Invalid representation-type <{t}>'
                    assert d.isdigit(), f'Invalid representation-digits <{d}>'

                    if t == 'a':
                        if not component.isalpha():
                            repr_errors.append('is not alphanumeric.')
                    if t == 'n':
                        if not re.match('\d*(\.|,)?\d+', component):
                            repr_errors.append('is not numeric.')
                    if t == 'an':
                        pass

                    if '..' in representation and not len(component) <= int(d):
                        repr_errors.append(f'repr: {representation},  max. len {d}')
                    if '..' not in representation and len(component) != int(d):
                        repr_errors.append(f'repr: {representation}, exact len {d}')

                    if repr_errors:
                        for e in repr_errors:
                            # print('    ERROR:', e)
                            lines.append('    ERROR:' + str(e))
                if not component and r['mc'] == 'M':
                    if not cd['representation'] is None:
                        lines.append(f'\n    Error, component <{code}> in segment {segment}')
        lines.append('')
    return '\n'.join(lines)


def make_edi_xml(segments: list, sd: dict, ed: dict, root_tag='EDIFACT') -> ElementTree.Element:
    root = ElementTree.Element(root_tag)
    for segment, data_elements in segments:
        if segment == 'UNA':
            ElementTree.SubElement(root, 'UNA').text = ''.join(data_elements)
            continue

        seg_element = ElementTree.SubElement(root, segment)
        name = sd[segment]['name']
        description = sd[segment]['description']
        table = sd[segment]['table']

        seg_element.attrib['description'] = description
        seg_element.attrib['name'] = name

        for d_i, data_element in enumerate(data_elements):
            data_element_tag = '%s%s' % (segment, d_i)
            data_sub_element = ElementTree.SubElement(seg_element, data_element_tag)

            pos = str((d_i+1)*10)
            cd = [r for r in table if r['pos'] and r['pos'].endswith(pos)][0]
            start = table.index(cd)

            if cd['representation'] is None:
                start += 1
                data_sub_element.attrib['pos'] = pos
                data_sub_element.attrib['code'] = cd['code']  # group code
                data_sub_element.attrib['name'] = cd['name']

            if cd['representation'] is not None and cd['pos'] is not None:
                data_sub_element.attrib['pos'] = pos

            if cd['repeat']:
                data_sub_element.attrib['repeat'] = str(cd['repeat'])
                data_sub_element.attrib['mc'] = cd['mc']

            for c_i, component in enumerate(data_element):
                component_tag = '%s%s%s' % (segment, d_i, c_i)
                component_sub_element = ElementTree.SubElement(data_sub_element, component_tag)
                if component:
                    component_sub_element.text = component

            for i_r, r in enumerate(table[start:]):
                if len(data_element) == i_r:
                    break
                c_code = r['code']
                c_component = data_element[i_r]
                c_name = r['name']
                c_mc = r['mc']
                c_repr = r['representation']

                data_sub_element[i_r].attrib = {
                    'code': c_code,
                    'name': c_name,
                    'mc': c_mc,
                    'representation': c_repr
                }
                if 'table' in ed[c_code] and c_component:
                    if c_component in ed[c_code]['table']:
                        data_sub_element[i_r].attrib['value'] = ed[c_code]['table'][c_component]['name']
                        data_sub_element[i_r].attrib['description'] = ed[c_code]['table'][c_component]['description']
                    else:
                        data_sub_element[i_r].attrib['value'] = 'CUSTOM CODE'
    return root


if __name__ == '__main__':
    import doctest
    doctest.testmod()
