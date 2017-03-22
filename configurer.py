import json

class WrongParameter(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self,*args,**kwargs)

def readJsonConfigFile(jsonFile):
    jsonStr = "\n".join([l for l in open(jsonFile, 'r').read().split("\n") if len(l) > 0 and not l.startswith("#")])

    #print "Json String", jsonStr
    
    return json.loads(jsonStr)

def loadFromJson(jsonFile, inParser, key1, key2, forbiddenKeys=('j', 'json', 'from_json', 'fromJson', 'J', 'to_json', 'toJson')):
    valids = []

    for action in inParser._actions:
        #print "action", action.option_strings, action.dest
        optionString = sorted(action.option_strings, key=lambda x: len(x))[-1] # get longest
        optionType   = action.type
        
        valids.extend([ (a.strip('-'), (optionType, optionString)) for a in action.option_strings])
        valids.append(  (action.dest , (optionType, optionString)) )

    valids = dict(valids)
    
    #print "valids dict", valids

    print "Loading Json", jsonFile
    
    pars = readJsonConfigFile(jsonFile)
    
    #print "Json Data", pars

    progs = pars.get(key1, None)

    if progs is None:
        print "No program data"
        raise WrongParameter("No program data", "no data for key 'programs'")
    
    ownPars = progs.get(key2, None)
    
    if ownPars is None:
        print "No gen_makefile data"
        raise WrongParameter("No gen_makefile data", "no data for key 'programs/gen_makefile'")
    
    progCmd = []
    
    for k, v in ownPars.items():
        if k in forbiddenKeys:
            continue
        
        if v is None:
            continue
        
        print " - {}: {}".format(k,v)
        
        if k not in valids:
            inParser.print_usage()
            inParser.print_help()
            err = "parameter '{}' is not valid. Possible parameters are {}".format(k, ", ".join(valids))
            raise WrongParameter("wrong parameter", err)
        
        kType, kStr = valids[k]

        if kType is None: # bool type
            progCmd.append(kStr)

        else: #other type
            if isinstance(v, list):
                for vv in v:
                    progCmd.append(kStr   )
                    progCmd.append(str(vv))
                
            else:
                progCmd.append(kStr  )
                progCmd.append(str(v))
    
    options = inParser.parse_args(progCmd)
    
    return options

def saveToJson(jsonFile, inParser, options, key1, key2, forbiddenKeys=('j', 'json', 'from_json', 'fromJson', 'J', 'to_json', 'toJson')):
    print "saving to {}".format(jsonFile)
    
    valids = {}
    for action in inParser._actions:
        # print "action", action.option_strings, action.dest, action.default
        valids[action.dest] = action.default
    
    vals = {}
    
    for k, v in vars(options).items():
        if v is None:
            continue
        
        if isinstance(v, list) and len(v) == 0:
            continue

        if v == valids[k]:
            continue
        
        if k in forbiddenKeys:
            continue
        
        print " - {}: {}".format(k,v)
        
        vals[k] = v

    data = {}
    if os.path.exists(jsonFile):
        print " config file ({}) exists. modifying".format(jsonFile)
        data = readJsonConfigFile(jsonFile)
    
    if key1 not in data: data[key1] = {}
    data[key1][key2] = vals
    
    json.dump(data, open(jsonFile, "w") , indent=1)
    
    print "done"
