from tests.enums.tools import Toolkit, CodeBaseTool

sonar_tools_test_data = [
    (
        Toolkit.CODEBASE_TOOLS,
        CodeBaseTool.SONAR,
        {
            "relative_url": "/api/issues/search",
            "params": '{"types":"CODE_SMELL","ps":"1"}',
        },
        """
            {
              "total" : 81,
              "p" : 1,
              "ps" : 1,
              "paging" : {
                "pageIndex" : 1,
                "pageSize" : 1,
                "total" : 81
              },
              "effortTotal" : 524,
              "issues" : [ {
                "key" : "AZhbHD1v-M-1Iu71H7sX",
                "rule" : "python:S107",
                "severity" : "MAJOR",
                "component" : "codemie:src/codemie/agents/langgraph_agent.py",
                "project" : "codemie",
                "line" : 50,
                "hash" : "52b8af6604f68ccfcc8d8ff425e1e389",
                "textRange" : {
                  "startLine" : 50,
                  "endLine" : 71,
                  "startOffset" : 8,
                  "endOffset" : 50
                },
                "flows" : [ ],
                "resolution" : "WONTFIX",
                "status" : "RESOLVED",
                "message" : "Method \"__init__\" has 21 parameters, which is greater than the 13 authorized.",
                "effort" : "20min",
                "debt" : "20min",
                "author" : "",
                "tags" : [ "brain-overload" ],
                "creationDate" : "2025-07-30T11:33:35+0000",
                "updateDate" : "2025-08-01T12:53:08+0000",
                "type" : "CODE_SMELL",
                "scope" : "MAIN",
                "quickFixAvailable" : false,
                "messageFormattings" : [ ],
                "codeVariants" : [ ],
                "cleanCodeAttribute" : "FOCUSED",
                "cleanCodeAttributeCategory" : "ADAPTABLE",
                "impacts" : [ {
                  "softwareQuality" : "MAINTAINABILITY",
                  "severity" : "MEDIUM"
                } ],
                "issueStatus" : "ACCEPTED",
                "prioritizedRule" : false
              } ],
              "components" : [ {
                "key" : "codemie:src/codemie/agents/langgraph_agent.py",
                "enabled" : true,
                "qualifier" : "FIL",
                "name" : "langgraph_agent.py",
                "longName" : "src/codemie/agents/langgraph_agent.py",
                "path" : "src/codemie/agents/langgraph_agent.py"
              }, {
                "key" : "codemie",
                "enabled" : true,
                "qualifier" : "TRK",
                "name" : "codemie",
                "longName" : "codemie"
              } ],
              "facets" : [ ]
            }
        """,
    ),
    (
        Toolkit.CODEBASE_TOOLS,
        CodeBaseTool.SONAR_CLOUD,
        {
            "relative_url": "/api/issues/search",
            "params": '{"types":"CODE_SMELL","ps":"1"}',
        },
        """
            {
              "total" : 15,
              "p" : 1,
              "ps" : 1,
              "paging" : {
                "pageIndex" : 1,
                "pageSize" : 1,
                "total" : 15
              },
              "effortTotal" : 127,
              "debtTotal" : 127,
              "issues" : [ {
                "key" : "AZTWg867SN_Wuz1X4Py2",
                "rule" : "kubernetes:S6892",
                "severity" : "MAJOR",
                "component" : "alezander86_python38g:deploy-templates/templates/deployment.yaml",
                "project" : "alezander86_python38g",
                "line" : 34,
                "hash" : "723c0daa435bdafaa7aa13d3ae06ca5e",
                "textRange" : {
                  "startLine" : 34,
                  "endLine" : 34,
                  "startOffset" : 19,
                  "endOffset" : 30
                },
                "flows" : [ ],
                "status" : "OPEN",
                "message" : "Specify a CPU request for this container.",
                "effort" : "5min",
                "debt" : "5min",
                "author" : "codebase@edp.local",
                "tags" : [ ],
                "creationDate" : "2024-11-07T13:14:43+0000",
                "updateDate" : "2025-02-05T14:28:27+0000",
                "type" : "CODE_SMELL",
                "organization" : "alezander86",
                "cleanCodeAttribute" : "COMPLETE",
                "cleanCodeAttributeCategory" : "INTENTIONAL",
                "impacts" : [ {
                  "softwareQuality" : "MAINTAINABILITY",
                  "severity" : "MEDIUM"
                }, {
                  "softwareQuality" : "RELIABILITY",
                  "severity" : "MEDIUM"
                } ],
                "issueStatus" : "OPEN",
                "projectName" : "python38g"
              } ],
              "components" : [ {
                "organization" : "alezander86",
                "key" : "alezander86_python38g:deploy-templates/templates/deployment.yaml",
                "uuid" : "AZTWg8uJSN_Wuz1X4Pye",
                "enabled" : true,
                "qualifier" : "FIL",
                "name" : "deployment.yaml",
                "longName" : "deploy-templates/templates/deployment.yaml",
                "path" : "deploy-templates/templates/deployment.yaml"
              }, {
                "organization" : "alezander86",
                "key" : "alezander86_python38g",
                "uuid" : "AZTWgJZiF0LopzvlIH8p",
                "enabled" : true,
                "qualifier" : "TRK",
                "name" : "python38g",
                "longName" : "python38g"
              } ],
              "organizations" : [ {
                "key" : "alezander86",
                "name" : "Taruraiev Oleksandr"
              } ],
              "facets" : [ ]
            }
        """,
    ),
]
