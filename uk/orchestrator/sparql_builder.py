import sparql_constants
import common_namespaces

def makeIRIRef(iri) -> str:
    return iri if common_namespaces.isNamespacedIRI(iri, \
        common_namespaces.default_prefixes) else '<' + iri + '>'

def makeVarRef(varName: str) -> str:
    return '?' + varName

def makeLiteralStr(valueStr: str, typeStr: str) -> str:
    return '"' + valueStr + '"^^' + typeStr

def make_prefix_str(namespace: str, url: str) -> str:
    return f"{sparql_constants.PREFIX} {namespace}: <{url}>"

class SPARQLWhereBuilder():

    def __init__(self):
        self._prefixes = {}
        self._vars = []
        self._wheres = []
        self._filter = ""
        self._optional_wheres = []

    def addPrefix(self, ans, aurl):
        self._prefixes[ans] = aurl
        return self

    def addVar(self, avar):
        self._vars.append(avar)
        return self

    def addWhere(self, asub, apred, aobj, optional: bool=False):
        if optional:
            self._optional_wheres.append([asub, apred, aobj])
        else:
            self._wheres.append([asub, apred, aobj])
        return self

    def addFilter(self, filter: str):
        self._filter = filter
        return self

    def autoAddPrefixes(self, apat, anss):
        """
        Iterates through a collection of triples and adds
        any of the provided namespaces, if they appear in the
        triples, as prefixes.
        """
        # Iterate through all triples in the pattern.
        for triple in apat:
            # Iterate through all three components of the triple.
            for s in triple:
                # Catch literals.
                parts = s.rsplit('^^', 1)
                pre_ns = parts[1] if len(parts) == 2 else s
                # Extract the string before any colon.
                ns = pre_ns.split(':', 1)[0]
                # If that string matches a known namespace...
                if ns in anss:
                    self.addPrefix(ns, anss[ns])

    def buildPattern(self, apat, optional: bool=False):
        pstrlist = []
        ## TODO: Separate multiple operations by semicolon,
        ## without repeating the subject.
        for triple in apat:
            pstr = " ".join(triple)
            if optional:
                pstr = f"{sparql_constants.OPTIONAL} {{{pstr}}}"
            pstrlist.append(pstr)
        return " . ".join(pstrlist)

    def build(self) -> str:
        if self._wheres or self._optional_wheres:
            strlist = []
            strlist.append(sparql_constants.WHERE + " {")
            if self._wheres:
                strlist.append(self.buildPattern(self._wheres))
                if self._filter != "":
                    strlist.append(sparql_constants.FILTER)
                    strlist.append(self._filter)
            if self._optional_wheres:
                if self._wheres:
                    strlist.append(".")
                strlist.append(self.buildPattern(self._optional_wheres,
                    optional=True))
            strlist.append("}")
            return " ".join(strlist)
        else:
            return ""

class SPARQLSelectBuilder(SPARQLWhereBuilder):

    def __init__(self):
        super().__init__()
        self._is_distinct = False
        self._limit = 0

    def set_distinct(self, distinct: bool=True) -> None:
        self._is_distinct = distinct

    def add_limit(self, limit: int) -> None:
        self._limit = limit

    def build(self, additional_prefixes: dict[str, str]={}):
        prefix_lib = common_namespaces.default_prefixes.copy()
        prefix_lib.update(additional_prefixes)
        self.autoAddPrefixes(self._wheres, prefix_lib)
        strlist = []
        for p in self._prefixes:
            strlist.append(make_prefix_str(p, self._prefixes[p]))
        strlist.append(sparql_constants.SELECT)
        if self._is_distinct:
            strlist.append(sparql_constants.DISTINCT)
        strlist.extend(self._vars)
        ## Build where block.
        strlist.append(super().build())
        if self._limit > 0:
            strlist.append(sparql_constants.LIMIT)
            strlist.append(str(self._limit))
        return " ".join(strlist)

class SPARQLUpdateBuilder(SPARQLWhereBuilder):

    def __init__(self):
        super().__init__()
        self._inserts = []
        self._deletes = []

    def addInsert(self, asub, apred, aobj):
        self._inserts.append([asub, apred, aobj])
        return self

    def addDelete(self, asub, apred, aobj):
        self._deletes.append([asub, apred, aobj])
        return self

    def build(self):
        strlist = []
        if self._inserts:
            self.autoAddPrefixes(self._inserts, common_namespaces.default_prefixes)
        if self._deletes:
            self.autoAddPrefixes(self._deletes, common_namespaces.default_prefixes)
        for p in self._prefixes:
            strlist.append(make_prefix_str(p, self._prefixes[p]))
        if self._deletes:
            strlist.append(sparql_constants.DELETE)
            if not self._wheres:
                strlist.append(sparql_constants.DATA)
            strlist.append("{")
            strlist.append(self.buildPattern(self._deletes))
            strlist.append("}")
        if self._inserts:
            if self._deletes:
                strlist.append(";")
            strlist.append(sparql_constants.INSERT)
            if not self._wheres:
                strlist.append(sparql_constants.DATA)
            strlist.append("{")
            strlist.append(self.buildPattern(self._inserts))
            strlist.append("}")
        ## Build where block.
        strlist.append(super().build())
        return " ".join(strlist)
