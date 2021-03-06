from numpy.lib.npyio import load
from . import toolbox
from re import search
from os import path


class CPDatSSI:
    def __init__(self, pr_database="/mnt/d/database/CPDat/CPDatRelease20201216/", version="20201216"):

        self.pr_database = pr_database
        self.version = version

        # load dataset
        self.p_chem_dict = pr_database + "chemical_dictionary_" + self.version + ".csv"
        self.p_presence_data = pr_database + "list_presence_data_" + self.version + ".csv"
        self.p_HHE_data = pr_database + "HHE_data_" + self.version + ".csv"
        self.p_doc_dict = pr_database + "document_dictionary_" + self.version + ".csv"
        self.p_list_presence = pr_database + "list_presence_dictionary_" + self.version + ".csv"
        self.p_PUC_dict = pr_database + "PUC_dictionary_" + self.version + ".csv"
        self.p_funct_used = pr_database + "functional_use_data_" + self.version + ".csv"
        self.p_product_compo = pr_database + "product_composition_data_" + self.version + ".csv"
        self.p_QSUR_data = pr_database + "QSUR_data_" + self.version + ".csv"
        self.p_fuctional_use_dict = pr_database + "functional_use_dictionary_" + self.version + ".csv" 

    def loadMapping(self):

        # check if folder exist
        if not path.isdir(self.pr_database):
            print("Folder included the CPDAT is not existing\tPlease define the variable 'pr_database'")

        self.d_chem_mapping = toolbox.loadMatrix(self.p_chem_dict, sep = ",")

        # PUC
        self.d_PUC = toolbox.loadMatrix(self.p_PUC_dict, sep = ",")

        # document ID with PUC
        l_doc_PUC = toolbox.loadMatrixToList(self.p_product_compo, sep = ",")

        self.d_PUC_map_chemical = {}
        for d_doc_PUC in l_doc_PUC:
            PUC_id = d_doc_PUC["puc_id"]
            kind_ID = self.d_PUC[PUC_id]["kind"]
            try: 
                self.d_PUC_map_chemical[d_doc_PUC["chemical_id"]]
            except:
                self.d_PUC_map_chemical[d_doc_PUC["chemical_id"]] = {}
                self.d_PUC_map_chemical[d_doc_PUC["chemical_id"]]["l_PUC_id"] = []
                self.d_PUC_map_chemical[d_doc_PUC["chemical_id"]]["kind"] = []
                
            if not PUC_id in self.d_PUC_map_chemical[d_doc_PUC["chemical_id"]]["l_PUC_id"] :
                self.d_PUC_map_chemical[d_doc_PUC["chemical_id"]]["l_PUC_id"].append(PUC_id)

            if not kind_ID in self.d_PUC_map_chemical[d_doc_PUC["chemical_id"]]["kind"] :
                self.d_PUC_map_chemical[d_doc_PUC["chemical_id"]]["kind"].append(kind_ID)

        # functionnal used        
        l_d_functionnal_used = toolbox.loadMatrixToList(self.p_fuctional_use_dict, sep = ",")
        d_functional_used_out = {}
        for d_functional_used in l_d_functionnal_used:
            chemical_id = d_functional_used["chemical_id"]
            try: d_functional_used_out[chemical_id]
            except:
                d_functional_used_out[chemical_id] = {}
                d_functional_used_out[chemical_id]["functional_use_id"] = []
                d_functional_used_out[chemical_id]["report_funcuse"] = []
                d_functional_used_out[chemical_id]["oecd_function"] = []
            d_functional_used_out[chemical_id]["functional_use_id"].append(d_functional_used["functional_use_id"])
            d_functional_used_out[chemical_id]["report_funcuse"].append(d_functional_used["report_funcuse"])
            d_functional_used_out[chemical_id]["oecd_function"].append(d_functional_used["oecd_function"])
        self.d_functional_used =  d_functional_used_out  

        # presence in dict
        self.d_list_presence = toolbox.loadMatrix(self.p_list_presence, sep = ",")
        
        l_presence_data = toolbox.loadMatrixToList(self.p_presence_data, sep = ",")
        self.d_presence_map = {}
        for d_presence_data in l_presence_data:
            chemical_id = d_presence_data["chemical_id"]
            document_id = d_presence_data["document_id"]
            presence_id = d_presence_data["list_presence_id"]
            try:self.d_presence_map[chemical_id]
            except: 
                self.d_presence_map[chemical_id] = {}
                self.d_presence_map[chemical_id]["l_document_id"] = []
                self.d_presence_map[chemical_id]["l_presence_id"] = []
            
            if not document_id in self.d_presence_map[chemical_id]["l_document_id"]:
                self.d_presence_map[chemical_id]["l_document_id"].append(document_id)
            if not presence_id in self.d_presence_map[chemical_id]["l_presence_id"]:
                self.d_presence_map[chemical_id]["l_presence_id"].append(presence_id)
        
        # load mapping from CASRN
        d_casrn = {}
        for chem in self.d_chem_mapping.keys():
            try:casrn = self.d_chem_mapping[chem]["preferred_casrn"]
            except: continue
            if casrn != "NA" and casrn != "":
                try:d_casrn[casrn].append(chem)
                except: d_casrn[casrn] = [chem]
        self.d_cas_mapping = d_casrn

        # load document ID
        self.d_document_by_id = toolbox.loadMatrix(self.p_doc_dict, sep = ",")
    
    def casrnToFunctions(self, casrn):
        """
        Use the chemical disctionnary but only pull together data from report used and oecd
        """
        # find the chem_id
        try:l_chem_id = self.d_cas_mapping[casrn]
        except: 
            return {"l_chem_id":[], "funcuse":[], "oecd_function":[], "l_presence_id":[], "l_document_id":[]}

        d_out = {"l_chem_id":[],"funcuse":[], "oecd_function":[], "l_presence_id":[], "l_document_id":[]}
        for chem_id in l_chem_id:
            d_out["l_chem_id"].append(chem_id)
            
            try: l_funuse = self.d_functional_used[chem_id]["report_funcuse"]
            except: l_funuse = []
            try:l_oecd = self.d_functional_used[chem_id]["oecd_function"]
            except: l_oecd = []
            try: l_presence_id = self.d_presence_map[chem_id]["l_presence_id"]
            except: l_presence_id = []
            try: l_document_id = self.d_presence_map[chem_id]["l_document_id"]
            except: l_document_id = []

            d_out["l_presence_id"] = d_out["l_presence_id"] + l_presence_id
            d_out["l_document_id"] = d_out["l_document_id"] + l_document_id

            for funuse in l_funuse:
                if not funuse.lower() in d_out["funcuse"]:
                    d_out["funcuse"].append(funuse.lower())

            for oecd in l_oecd:
                if not oecd.lower() in d_out["oecd_function"]:
                    d_out["oecd_function"].append(oecd.lower())

        return d_out

    def listCasToFunct(self, l_casrn):
        """
        Build a dictionnary with the CASRN as key and value from the cpdat
        """
        d_out = {}

        for CASRN in l_casrn:
            d_exposure = self.casrnToFunctions(CASRN)
            d_out[CASRN] = d_exposure

        self.d_casrn_mapped = d_out
        return d_out

    def extractBoardExposure(self, p_filout = "", p_temp = ""):
        """
        From Cardona 2021 script
        List of function [Pesticides, Industrial, Consumer products, Diet, Pharmaceuticals, No data]
        """
        
        d_out = {}
        if not "d_casrn_mapped" in self.__dict__:
            print("== Load CPDAT first with the list of CASRN ==")
            return 
            
        # main output
        if p_filout != "":
            filout = open(p_filout, "w")
            filout.write("CASRN\tchemical_id\tfunction_used\toecd\tpresence_name\tpresence_definition\tPUC\tclass_combine\n")

        # temporary file
        if p_temp != "":
            ftemp = open(p_temp, "w")
            ftemp.write("CASRN\tl_chem_id\tUsed\toecd\tl_presence_id\tl_presence_name\tl_presence_def\tl_PUC\n")

        for casrn in self.d_casrn_mapped.keys():
            d_out[casrn] = []
            if self.d_casrn_mapped[casrn]["l_chem_id"] == []:
                if p_filout != "":
                    filout.write("%s\tNA\tNA\tNA\tNA\tNA\tNA\tNo data\n"%(casrn))
                continue
            
            # define as a string
            self.d_casrn_mapped[casrn]["funcuse"] = "----".join(self.d_casrn_mapped[casrn]["funcuse"])
            self.d_casrn_mapped[casrn]["oecd_function"] = "----".join(self.d_casrn_mapped[casrn]["oecd_function"])
            
            l_funct_from_funcuse = self.searchBoardExposureInFuncUseAndOECDFunc(self.d_casrn_mapped[casrn]["funcuse"])
            l_funct_from_oecd = self.searchBoardExposureInFuncUseAndOECDFunc(self.d_casrn_mapped[casrn]["oecd_function"])

            l_presence = []
            l_def_presence = []
            l_doc_title = []
            l_doc_exp = []
            l_cas_exp = self.individualMappingOnBoardExp(casrn)
            l_PUC_exp = []
            l_PUC = []

            #PUC -- when PUC add in Consumer products
            for chemical_id in self.d_casrn_mapped[casrn]["l_chem_id"]:
                try:
                    self.d_PUC_map_chemical[chemical_id]
                except:
                    continue
                l_PUC_exp.append("Consumer products")
                l_PUC = l_PUC + self.d_PUC_map_chemical[chemical_id]["kind"]
                if "O" in self.d_PUC_map_chemical[chemical_id]["kind"]:
                    l_PUC_exp.append("Industrial")

            # remove duplicate PUC
            l_PUC = list(set(l_PUC))
            l_PUC_exp = list(set(l_PUC_exp))

            # presence ID
            for presence_id in self.d_casrn_mapped[casrn]["l_presence_id"]:
                if presence_id == "NA":
                    continue
                l_presence.append(self.d_list_presence[presence_id]["name"])
                l_def_presence.append(self.d_list_presence[presence_id]["definition"])

            # remove duplication
            l_presence = list(set(l_presence))
            l_def_presence = list(set(l_def_presence))

            l_funct_from_presence_name = self.searchBoardExposureInPresenceList(",".join(l_presence))
            l_funct_from_presence_def = self.searchBoardExposureInPresenceList(",".join(l_def_presence))

            # add in the d-out dictionnary
            d_out[casrn] = d_out[casrn] + l_funct_from_funcuse + l_funct_from_oecd + l_funct_from_presence_name + l_funct_from_presence_def + l_doc_exp + l_cas_exp + l_PUC_exp
            d_out[casrn] = list(set(d_out[casrn]))

            if d_out[casrn] == []:
                d_out[casrn] = ["No data"]

            if p_filout != "":
                filout.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(casrn, "-".join(self.d_casrn_mapped[casrn]["l_chem_id"]), "+".join(l_funct_from_funcuse), "+".join(l_funct_from_oecd), "+".join(l_funct_from_presence_name), "+".join(l_funct_from_presence_def), "+".join(l_PUC_exp), "+".join(d_out[casrn])))

            if p_temp != "":
                ftemp.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(casrn,"----".join(self.d_casrn_mapped[casrn]["l_chem_id"]), self.d_casrn_mapped[casrn]["funcuse"], self.d_casrn_mapped[casrn]["oecd_function"], "----".join(self.d_casrn_mapped[casrn]["l_presence_id"]), "----".join(l_presence), "----".join(l_def_presence), "----".join(l_PUC)))

        if p_filout != "":
            filout.close()

        if p_temp != "":
            ftemp.close()
        
        self.d_board_exp = d_out
        return d_out

    def searchBoardExposureInPresenceList(self, str_in):
        l_funct = []
        str_in = str_in.lower()
        #Pesticide
        if search("pesticide", str_in):
            l_funct.append("Pesticides")

        #Diet
        if search("animal_products", str_in):
            l_funct.append("Diet")
        if search("baby_food", str_in):
            l_funct.append("Diet")
        if search("CEDI", str_in):
            l_funct.append("Diet")
        if search("EAFUS", str_in):
            l_funct.append("Diet")
        if search("dairy", str_in):
            l_funct.append("Diet")
        if search("drinking_water", str_in):
            l_funct.append("Diet")            
        if search("food_additive", str_in):
            l_funct.append("Diet")
        if search("fruits", str_in):
            l_funct.append("Diet")
        if search("general_foods", str_in):
            l_funct.append("Diet")
        if search("grain", str_in):
            l_funct.append("Diet")
        if search("legumes", str_in):
            l_funct.append("Diet")
        if search("nuts", str_in):
            l_funct.append("Diet")
        if search("tobacco", str_in):
            l_funct.append("Diet")
        if search("supplements", str_in):
            l_funct.append("Diet")
        if search("food contact", str_in):
            l_funct.append("Diet")
        
        #Consumer products
        if search("arts", str_in):
            l_funct.append("Consumer products")
        if search("cotton", str_in):
            l_funct.append("Consumer products")
        if search("cleaning product", str_in):
            l_funct.append("Consumer products")
        if search("consumer", str_in):
            l_funct.append("Consumer products")
        if search("furniture", str_in):
            l_funct.append("Consumer products")
        if search("furnishing", str_in):
            l_funct.append("Consumer products")
        if search("electronics", str_in):
            l_funct.append("Consumer products")
        if search("personal care", str_in):
            l_funct.append("Consumer products")
        if search("vehicle", str_in):
            l_funct.append("Consumer products")
        if search("toys", str_in):
            l_funct.append("Consumer products")
        if search("Substances in", str_in):
            l_funct.append("Consumer products")
        if search("IFRA", str_in):
            l_funct.append("Consumer products")
        if search("children", str_in):
            l_funct.append("Consumer products")
        if search("children", str_in):
            l_funct.append("Consumer products")
        if search("food contact", str_in):
            l_funct.append("Consumer products")

        ### Industrial
        if search("construction", str_in):
            l_funct.append("Industrial")
        if search("home maintenance", str_in):
            l_funct.append("Industrial")
        if search("yard", str_in):
            l_funct.append("Industrial")
        if search("plastic additive", str_in):
            l_funct.append("Industrial")
        if search("fossil fuel", str_in):
            l_funct.append("Industrial")
        if search("fracking", str_in):
            l_funct.append("Industrial")   
        if search("manufacturing", str_in):
            l_funct.append("Industrial")
            
        ### pharmaceutical
        if search("pharmaceutical", str_in):
            l_funct.append("Pharmaceuticals")
            
        ### Environmental
        if str_in == "air":
           l_funct.append("Environmental") 
        if search(" air ", str_in):
            l_funct.append("Environmental")
        if search("agricul", str_in):
            l_funct.append("Environmental")
        if search("soil", str_in):
            l_funct.append("Environmental")
        if search("water", str_in) and not search("drinking", str_in):
            l_funct.append("Environmental")
        if search("emission", str_in):
            l_funct.append("Environmental")    

        return list(set(l_funct))

    def searchBoardExposureInFuncUseAndOECDFunc(self, str_in):
        l_funct = []
        str_in = str_in.lower()
        #Pesticide
        if search("pesticide", str_in):
            l_funct.append("Pesticides")
        if search("antimicrobial", str_in):
            l_funct.append("Pesticides")
        if search("fungicide", str_in):
            l_funct.append("Pesticides")
        if search("extermination", str_in): 
            l_funct.append("Pesticides")
        if search("herbicide", str_in):
            l_funct.append("Pesticides")
        if search("insecticide", str_in):
            l_funct.append("Pesticides")

        #Industrial
        if search("industrial", str_in): 
            l_funct.append("Industrial")
        if search("NACE", str_in):
            l_funct.append("Industrial")
        if search("coal tar", str_in):
            l_funct.append("Industrial")  
        if search("raw material", str_in):
            l_funct.append("Industrial")
        if search("battery fluid", str_in):
            l_funct.append("Industrial")
        if search("silicon fluid", str_in):
            l_funct.append("Industrial")
        if search("silicone fluid", str_in):
            l_funct.append("Industrial")
        if search(" mining", str_in):
            l_funct.append("Industrial")
        if search("manufacturing", str_in):
            l_funct.append("Industrial")
        if search("rubber", str_in):
            l_funct.append("Industrial")
        if search("plasticizer", str_in):
            l_funct.append("Industrial")
        if search("plasticiser", str_in):
            l_funct.append("Industrial")
        if search("catalyst", str_in):
            l_funct.append("Industrial")
        if search("uv stabilizer", str_in):
            l_funct.append("Industrial")        
        if search("flame retardant", str_in):
            l_funct.append("Industrial")
        if search("colorant", str_in):
            l_funct.append("Industrial") 
        if search("electronic", str_in):
            l_funct.append("Industrial")

        #environmental
        if search("agricul", str_in):
            l_funct.append("Environmental")
        if search("emission", str_in):
            l_funct.append("Environmental")
        if search("soil", str_in):
            l_funct.append("Environmental")
        if search("water", str_in) and not search("drinking", str_in):
            l_funct.append("Environmental")
        
        
        # diet
        if search("food", str_in) and not search("not for food", str_in) and not search("Nonfood", str_in):
            l_funct.append("Diet")
        if search("beverage", str_in):
            l_funct.append("Diet")
        if search("drinking", str_in):
            l_funct.append("Diet")
        if search("flavouring", str_in):
            l_funct.append("Diet")
        if search("food contact", str_in):
            l_funct.append("Diet")
        
        #Pharmaceutical
        if search("drug", str_in):
            l_funct.append("Pharmaceuticals")
        if search("pharma", str_in):
            l_funct.append("Pharmaceuticals")


        #Consumer products
        if search("apparel", str_in):
            l_funct.append("Consumer products")
        if search("personal care", str_in):
            l_funct.append("Consumer products")
        if search("arts craft", str_in):
            l_funct.append("Consumer products")
        if search("furniture", str_in): 
            l_funct.append("Consumer products")
        if search("child use", str_in):
            l_funct.append("Consumer products")
        if search("decor", str_in):
            l_funct.append("Consumer products")
        if search("toy", str_in):
            l_funct.append("Consumer products")
        if search("antimicrobial", str_in):
            l_funct.append("Consumer products")
        if search("electronic", str_in):
            l_funct.append("Consumer products")
        if search(" garden ", str_in):
            l_funct.append("Consumer products")
        if search("sports equipment", str_in):
            l_funct.append("Consumer products")
        if search(" baby ", str_in):
            l_funct.append("Consumer products")
        if search(" pet ", str_in):
            l_funct.append("Consumer products")
        if search(" pets ", str_in):
            l_funct.append("Consumer products")    
        if search(" dogs ", str_in):
            l_funct.append("Consumer products")
        if search(" cats ", str_in):
            l_funct.append("Consumer products")
        if search(" tools", str_in):
            l_funct.append("Consumer products")
        if search("dental", str_in):
            l_funct.append("Consumer products")
        if search("toothbrush", str_in):
            l_funct.append("Consumer products")
        if search("soap", str_in):
            l_funct.append("Consumer products")
        if search("automotive", str_in):
            l_funct.append("Consumer products")
        if search("hair dyeing", str_in):
            l_funct.append("Consumer products")
        if search("skin-care", str_in):
            l_funct.append("Consumer products")
        if search("hair conditioning", str_in):
            l_funct.append("Consumer products")
        if search("shampoo", str_in):
            l_funct.append("Consumer products") 
        if search("cosmetic", str_in):
            l_funct.append("Consumer products")
        if search("perfuming", str_in):
            l_funct.append("Consumer products")
        if search("perfume", str_in):
            l_funct.append("Consumer products")
        if search("flame retardant", str_in):
            l_funct.append("Consumer products")
        if search("personal care", str_in):
            l_funct.append("Consumer products")
        if search("skin conditioning", str_in):
            l_funct.append("Consumer products")
        if search("sunscreen agent", str_in):
            l_funct.append("Consumer products")
        if search("coal tar", str_in):
            l_funct.append("Consumer products") 
        if search("colorant", str_in):
            l_funct.append("Consumer products") 
        if search("food contact", str_in):
            l_funct.append("Consumer products")

        return list(set(l_funct))

    def mapDocumentToBoardExp(self, document_ID):

        ##Air Water INC Fine Chemicals List
        if document_ID == "1373515":
            return ["Industrial"]

        ##Fl@vis Flavouring Substances
        if document_ID == "1513117":
            return ["Diet"]

        ##U.S. FDA list of Indirect Additives used in Food Contact Substances; presence of a substance in this list indicates that only certain intended uses and use conditions are authorized by FDA regulations (version of list updated 10/4/2018)
        if document_ID == "460":
            return ["Diet"]

        ##Indirect Additives used in Food Contact Substances
        if document_ID == "1372213":
            return ["Pesticides"]

        ##Inert Ingredients Permitted for Use in Nonfood Use Pesticide Products
        if document_ID == "1365244":
            return ["Pesticides"]  

        ##2007 Pesticide Residues in Blueberries
        if document_ID == "1374900":
            return ["Pesticides"] 


        ##Harmonized Tariff Schedule of the United States (2019) Intermediate Chemicals for Dyes Appendix
        if document_ID == "1371498":
            return ["Consumer products"]

        ##present on the WA State Department of Ecology - Chemicals of High Concern to Children Reporting List (version of list pulled 4/24/2020),pertaining to  or intended for use specifically by children
        if document_ID == "453478":
            return ["Consumer products", "Industrial"]
        
        ##chemicals measured or identified in environmental media or products,Sources specific to a European country or subset of countries,writing utensils containing liquid or gel ink
        if document_ID == "400407471":
            return ["Consumer products"]

        #substances on the International Fragrance Association's ordered register of all fragrance ingredients used in consumer goods by the fragrance industry's customers worldwide
        if document_ID == "519":
            return ["Consumer products", "Industrial"]

        ##applied to all data sources used in MN DoH chemical screening proof of concept,chemicals measured or identified in environmental media or products,water intended for drinking  or related to drinking water; includes bottled water  finished water from drinking water treatment plants  and untreated water that has been denoted as a drinking source
        if document_ID == "392400422":
            return ["Pesticides", "Diet"]

        ## Relating to pesticides or pesticide usage. Includes specific types of pesticides  e.g. insecticides   herbicides  fungicides  and fumigants; also includes general biocides,chemical residues  typically from drugs or pesticides
        if document_ID == "423446":
            return ["Pesticides", "Pharmaceuticals"]       

        ##chemicals measured or identified in environmental media or products,Relating to pesticides or pesticide usage. Includes specific types of pesticides  e.g. insecticides   herbicides  fungicides  and fumigants; also includes general biocides,general term pertaining to agricultural practices  including the raising and farming of animals and growing of crops,includes fresh  canned and frozen forms  as well as juices and sauces (e.g. applesauce)  excludes forms intended for consumption by young children (i.e. baby foods); includes green beans and peas,chemical residues  typically from drugs or pesticides
        if document_ID == "400423425442446":
            return ["Pesticides", "Pharmaceuticals"] 

        ##Pharmaceutical Appendix (2019) Table 1
        if document_ID == "1372195":
            return ["Pharmaceuticals"]

        ##Pharmaceutical Appendix (2019) Table 3
        if document_ID == "1372197":
            return ["Pharmaceuticals"]        

        return []
    
    def individualMappingOnBoardExp(self, casrn):
        
        if casrn == "87818-31-3":
            return ["Pesticides"]

        if casrn == "4291-63-8":
            return ["Pharmaceuticals"]

        return []

    def comparisonBoardExposureWithCardona2021(self, p_board_exp, p_csv_cardona2021, pr_out):

        l_d_cardona = toolbox.loadMatrixToList(p_csv_cardona2021, sep = ",")
        d_board_exp = toolbox.loadMatrix(p_board_exp)

        d_out = {}
        for casrn in d_board_exp.keys():
            d_out[casrn] = {}
            d_out[casrn]["cardona2021"] = []
            d_out[casrn]["board_exp"] = []
            d_out[casrn]["aggred"]  = "0"


            exposure = d_board_exp[casrn]["class_combine"]
            d_out[casrn]["board_exp"] = exposure.split("-")
            d_out[casrn]["board_exp"] = list(set(d_out[casrn]["board_exp"]))

            for d_cardona in l_d_cardona:
                casrn_cardona = d_cardona["CASN_protect"].replace(" ", "")
                if casrn == casrn_cardona:
                    if d_cardona["Consumer"] == "1" or d_cardona["Consumer"] == "1*":
                        d_out[casrn]["cardona2021"].append("Consumer products")
                    if d_cardona["Diet"] == "1" or d_cardona["Diet"] == "1*":
                        d_out[casrn]["cardona2021"].append("Diet")
                    if d_cardona["Industrial"] == "1" or d_cardona["Industrial"] == "1*":
                        d_out[casrn]["cardona2021"].append("Industrial")
                    if d_cardona["Pest."] == "1" or d_cardona["Pest."] == "1*":
                        d_out[casrn]["cardona2021"].append("Pesticides")
                    if d_cardona["Pharma."] == "1" or d_cardona["Pharma."] == "1*":
                        d_out[casrn]["cardona2021"].append("Pharmaceuticals")
                    if d_cardona["No exposure source data"] == "1" or d_cardona["No exposure source data"] == "1*":
                        d_out[casrn]["cardona2021"].append("No data")
                    
                    d_out[casrn]["cardona2021"] = list(set(d_out[casrn]["cardona2021"]))
                    if d_out[casrn]["cardona2021"] == d_out[casrn]["board_exp"]:
                        d_out[casrn]["aggred"] = "1"
            
        # write in file
        p_filout = pr_out + "overlapCardonaCPDATMap.csv"
        filout = open(p_filout, "w")
        filout.write("CASRN\tCardonaList\tMappingList\tAggree\n")

        for casrn in d_out.keys():
            filout.write("%s\t%s\t%s\t%s\n"%(casrn, "-".join(d_out[casrn]["cardona2021"]), "-".join(d_out[casrn]["board_exp"]), d_out[casrn]["aggred"]))
        filout.close()


