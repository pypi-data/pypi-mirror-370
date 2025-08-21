@testing_solution
@yaml
Feature: Test YAML module

    @load_file
    Scenario: Load a YAML file
        Given FILE_PATH = create file with name 'load.yaml'
            """
            company: spacelift
            domain:
             - devops
             - devsecops
            tutorial:
              - yaml:
                  name: "YAML Ain't Markup Language"
                  type: awesome
                  born: 2001
              - json:
                  name: JavaScript Object Notation
                  type: great
                  born: 2001
              - xml:
                  name: Extensible Markup Language
                  type: good
                  born: 1996
            author: omkarbirade
            """
            
        When CONTENT = load YAML file FILE_PATH
        
        Given TABLE = convert json CONTENT to name/value table with names and list uncollapsed
        Then table TABLE is
            | Name                    | Value                        |
            | 'author'                | 'omkarbirade'                |
            | 'company'               | 'spacelift'                  |
            | 'domain[0]'             | 'devops'                     |
            | 'domain[1]'             | 'devsecops'                  |
            | 'tutorial[0].yaml.born' | 2001                         |
            | 'tutorial[0].yaml.name' | 'YAML Ain't Markup Language' |
            | 'tutorial[0].yaml.type' | 'awesome'                    |
            | 'tutorial[1].json.born' | 2001                         |
            | 'tutorial[1].json.name' | 'JavaScript Object Notation' |
            | 'tutorial[1].json.type' | 'great'                      |
            | 'tutorial[2].xml.born'  | 1996                         |
            | 'tutorial[2].xml.name'  | 'Extensible Markup Language' |
            | 'tutorial[2].xml.type'  | 'good'                       |

    @base_load_file
    Scenario: Load a YAML file with only base YAML features
        Given FILE_PATH = create file with name 'load.yaml'
            """
            company: spacelift
            domain:
             - devops
             - devsecops
            tutorial:
              - yaml:
                  name: "YAML Ain't Markup Language"
                  type: awesome
                  born: 2001
              - json:
                  name: JavaScript Object Notation
                  type: great
                  born: 2001
              - xml:
                  name: Extensible Markup Language
                  type: good
                  born: 1996
            author: omkarbirade
            """
            
        When CONTENT = load YAML file FILE_PATH (with only strings)
        
        Given TABLE = convert json CONTENT to name/value table with names and list uncollapsed
        Then table TABLE is
            | Name                    | Value                        |
            | 'author'                | 'omkarbirade'                |
            | 'company'               | 'spacelift'                  |
            | 'domain[0]'             | 'devops'                     |
            | 'domain[1]'             | 'devsecops'                  |
            | 'tutorial[0].yaml.born' | '2001'                       |
            | 'tutorial[0].yaml.name' | 'YAML Ain't Markup Language' |
            | 'tutorial[0].yaml.type' | 'awesome'                    |
            | 'tutorial[1].json.born' | '2001'                       |
            | 'tutorial[1].json.name' | 'JavaScript Object Notation' |
            | 'tutorial[1].json.type' | 'great'                      |
            | 'tutorial[2].xml.born'  | '1996'                       |
            | 'tutorial[2].xml.name'  | 'Extensible Markup Language' |
            | 'tutorial[2].xml.type'  | 'good'                       |

    @full_load_file
    Scenario: Load a YAML file with full YAML features
        Given FILE_PATH = create file with name 'load.yaml'
            """
            company: spacelift
            domain:
             - devops
             - devsecops
            tutorial:
              - yaml: &reference
                  name: "YAML Ain't Markup Language"
                  type: awesome
                  born: 2001
              - json: *reference
              - xml:
                  <<: *reference
                  born: 1996
            author: omkarbirade
            """
            
        When CONTENT = load YAML file FILE_PATH (with full YAML features)
        
        Given TABLE = convert json CONTENT to name/value table with names and list uncollapsed
        Then table TABLE is
            | Name                    | Value                        |
            | 'author'                | 'omkarbirade'                |
            | 'company'               | 'spacelift'                  |
            | 'domain[0]'             | 'devops'                     |
            | 'domain[1]'             | 'devsecops'                  |
            | 'tutorial[0].yaml.born' | 2001                         |
            | 'tutorial[0].yaml.name' | 'YAML Ain't Markup Language' |
            | 'tutorial[0].yaml.type' | 'awesome'                    |
            | 'tutorial[1].json.born' | 2001                         |
            | 'tutorial[1].json.name' | 'YAML Ain't Markup Language' |
            | 'tutorial[1].json.type' | 'awesome'                    |
            | 'tutorial[2].xml.born'  | 1996                         |
            | 'tutorial[2].xml.name'  | 'YAML Ain't Markup Language' |
            | 'tutorial[2].xml.type'  | 'awesome'                    |


    @load_multiple_document
    Scenario: Load a multiple document YAML file
        Given FILE_PATH = create file with name 'load_multiple.yaml'
            """
            ---
            company: spacelift
            domain:
             - devops
             - devsecops
            ---
            tutorial:
              - yaml:
                  name: "YAML Ain't Markup Language"
                  type: awesome
                  born: 2001
              - json:
                  name: JavaScript Object Notation
                  type: great
                  born: 2001
              - xml:
                  name: Extensible Markup Language
                  type: good
                  born: 1996
            author: omkarbirade
            ...
            """
            
        When CONTENT = load multiple documents YAML file FILE_PATH
        
        Given TABLE_1 = convert json CONTENT[0] to name/value table with names and list uncollapsed
        Given TABLE_2 = convert json CONTENT[1] to name/value table with names and list uncollapsed
        Then table TABLE_1 is
            | Name                    | Value                        |
            | 'company'               | 'spacelift'                  |
            | 'domain[0]'             | 'devops'                     |
            | 'domain[1]'             | 'devsecops'                  |
        Then table TABLE_2 is
            | Name                    | Value                        |
            | 'author'                | 'omkarbirade'                |
            | 'tutorial[0].yaml.born' | 2001                         |
            | 'tutorial[0].yaml.name' | 'YAML Ain't Markup Language' |
            | 'tutorial[0].yaml.type' | 'awesome'                    |
            | 'tutorial[1].json.born' | 2001                         |
            | 'tutorial[1].json.name' | 'JavaScript Object Notation' |
            | 'tutorial[1].json.type' | 'great'                      |
            | 'tutorial[2].xml.born'  | 1996                         |
            | 'tutorial[2].xml.name'  | 'Extensible Markup Language' |
            | 'tutorial[2].xml.type'  | 'good'                       |


    @save_file
    Scenario: Save data in a YAML file
        Given DATA = ${{'company': 'spacelift', 'domain': ['devops', 'devsecops'], 'tutorial': [{'yaml': {'name': "YAML Ain't Markup Language", 'type': 'awesome', 'born': 2001}}, {'json': {'name': 'JavaScript Object Notation', 'type': 'great', 'born': 2001}}, {'xml': {'name': 'Extensible Markup Language', 'type': 'good', 'born': 1996}}], 'author': 'omkarbirade'}}
        
        Given FILE_PATH = path to file with name 'save.yaml'
        When save DATA in YAML file FILE_PATH
        
        Given CONTENT_BYTES = content of file FILE_PATH
        Given CONTENT_STR = convert object value CONTENT_BYTES to string
        Given CONTENT_STR = ${CONTENT_STR.strip()}
        
        Given EXPECTED = multiline text
            """
            author: omkarbirade
            company: spacelift
            domain:
            - devops
            - devsecops
            tutorial:
            - yaml:
                born: 2001
                name: YAML Ain't Markup Language
                type: awesome
            - json:
                born: 2001
                name: JavaScript Object Notation
                type: great
            - xml:
                born: 1996
                name: Extensible Markup Language
                type: good
            """
        Then CONTENT_STR == EXPECTED





