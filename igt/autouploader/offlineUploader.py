'''
Created on Jan 22, 2016

Last Changes May 5, 2016

@author: fnavarro, emiramon
@contact: florencio.navarro@intel.com, jairo.daniel.miramontes.caton@intel.com
'''
import subprocess,csv, json, platform, urllib, os, sys
import ConfigParser
from optparse import OptionParser
from datetime import *
from pymongo import MongoClient

currentEnv = 'sand'

sandUrl = 'http://qa_reports-tech.otcqa.jf.intel.com/gfx-sand/api/import?'
sandKey = '20831df0eb195cc64f9f'

prodUrl ='https://otcqarpt.jf.intel.com/gfx/api/import?'
prodKey ='3eb91850d33f10b98ac2'


class Device(object):
    
    def __init__(self):
        self.kernel =platform.uname()[2]
        self.arch = platform.architecture()[0].split('b')[0]+" bits"
        self.pc_model = "cat /proc/cpuinfo |  grep 'model name' | head -n 1 | awk -F ': '  '{print $2}' "
        self.pc_family = "sudo dmidecode -t 4 |  grep 'Family:' | awk '{print $2}' "
        self.vga_controller = "sudo lspci |  grep 'VGA compatible controller' | head -n 1 | awk -F ': '  '{print $2}' "
        self.vga_driver = "sudo lspci -v -s $(lspci | grep 'VGA compatible controller' | cut  -d' ' -f 1)|  grep 'Kernel driver in use' | awk -F  ': ' '{print $2}' "
        self.bios_version = "sudo dmidecode | grep 'BIOS Revision:' | awk '{print $3}' "
        self.fw_version = "sudo dmidecode -t 0 |  grep 'Version:' | awk -F ': '  '{print $2}' "
        self.memory = "vmstat -s |  grep 'total memory' |  awk '{print $1}' "
        self.manufacturer = "sudo dmidecode -t 1 |  grep 'Manufacturer:' | awk '{print $2}' "
        self.mb_model = "sudo dmidecode -t 1 |  grep 'Product Name:' | awk -F ': '  '{print $2}' "
        self.mb_type = "sudo dmidecode -t 2 |  grep 'Type:' | awk -F ': '  '{print $2}' "
        self.pf_type ="sudo dmidecode -t 3 |  grep 'Type:' | awk -F ': '  '{print $2}' "
        self.os_version = platform.dist()
        self.env = platform.platform()

class DeviceInfo(Device):

    def get_output(self,opt):
        if len(opt) >= 20:
            option = opt
            proc = subprocess.Popen(option, stdout=subprocess.PIPE, shell=True)
        else:
            self.opt = opt
            proc = subprocess.Popen(self.opt, stdout=subprocess.PIPE, shell=True)
            
        (out, err) = proc.communicate()
        self.out = out
        return self.out

    def get_info(self,opt):
        #Use DRY to perfom a bucle of commands             
        if opt != "all":
            self = self.get_output(getattr(self, opt))
            return self
        else: 
            self.pc_model = self.get_output(self.pc_model)
            self.pc_family = self.get_output(self.pc_family)
            self.vga_controller = self.get_output(self.vga_controller)
            self.vga_driver = self.get_output(self.vga_driver)
            self.bios_version = self.get_output(self.bios_version)
            self.fw_version = self.get_output(self.fw_version)
            self.memory = self.get_output(self.memory)
            self.manufacturer = self.get_output(self.manufacturer)
            self.mb_model = self.get_output(self.mb_model)
            self.mb_type = self.get_output(self.mb_type)
            self.pf_type = self.get_output(self.pf_type)
            if self.memory != "":
                self.memory = str(int(self.memory)/1024)+" MB\n"
            else: self.memory = "No data"
            
            return self
        ## JAIRO the lines below can be replaced with returning the object SELF
        
class TrcReport():    
    def __init__(self):
        self.profile = ""
        self.build_id = ""
        self.total_cases = 0
        self.title = ""
        self.created_at = ""
        self.total_measured = 0
        self.total_pass = 0
        self.updated_at = ""
        self.tested_at = ""  
        self.release = ""
        self.hardware = ""
        self.weeknum = ""
        self.qa_id = ""
        self.total_fail = 0
        self.testtype = ""
        self.total_na = 0
        self.qa_summary_txt = ""
        self.features = ""
        self.image = ""
        #test_environment = hardware
        #environment_summary would be uploaded to qa_summary_txt"

class Feature():
    def __init__(self):
        self.cases = []
        self.name = ""#name of the results.csv
        self.total_measured = 0
        self.total_na = 0
        self.total_cases = 0
        self.total_pass = 0
        self.comments = ""
        self.total_fail = 0
        
class Case():
    def __init__(self):        
        self.status = ""
        self.comment= ""
        self.component = ""
        self.name = ""
        self.bug = ""
       

class Database():
    
    def __init__(self):
        self.client = MongoClient("10.64.95.35", 27017)
        
    def connect(self,opt):
        self.db = getattr(self.client, opt)
        return self.db
# Production Target https://otcqarpt.jf.intel.com/gfx/api/import?     #3eb91850d33f10b98ac2
# Sandbox Target http://qa_reports-tech.otcqa.jf.intel.com/gfx-sand/api/import?   #20831df0eb195cc64f9f

#'http://qa_reports-tech.otcqa.jf.intel.com/gfx-sand/api/import?'
class Uploader():
    def __init__(self):
        if(currentEnv == 'prod'):
            self.url_target = prodUrl            
            self.auth_token = prodKey            
        if(currentEnv == 'sand'):
            self.url_target = sandUrl            
            self.auth_token = sandKey            
        
        self.fields = TrcReport()
        
    def set_fields(self, results_file, release, platform, title, suite):
            currentTime = datetime.today()
            optPlatform = DeviceInfo()
            
            #Call the set_results function
            self.set_results(results_file, suite)
            
            #Take the parameters given by the user
            self.fields.profile = platform
            self.fields.title =  platform +" "+self.fields.testtype+" "+title
            self.fields.release = release
            self.fields.hardware = title
            self.fields.build_id = optPlatform.arch
            optPlatform.get_info("all")
            self.fields.qa_summary_txt = optPlatform.env+", "
            self.fields.qa_summary_txt += "Processor Model Family :  "+optPlatform.pc_model.strip()+"  "+optPlatform.pc_family.strip()+" Memory : "+optPlatform.memory
            self.fields.qa_summary_txt += "VGA Controller & Driver : "+optPlatform.vga_controller.strip()+", "+optPlatform.vga_driver
            self.fields.qa_summary_txt += "BIOS & Firmware Version  : "+optPlatform.bios_version.strip()+", "+optPlatform.fw_version
            self.fields.qa_summary_txt += "Platform Manufacturer & Type : "+optPlatform.manufacturer.strip()+", "+optPlatform.pf_type
            self.fields.qa_summary_txt += "Motherboard Model & Type : "+optPlatform.mb_model.strip()+", "+optPlatform.mb_type   
            self.fields.qa_summary = optPlatform.os_version[0]+" "+optPlatform.os_version[1]+" "+optPlatform.os_version[2] 
            self.fields.created_at = currentTime
            self.fields.updated_at = currentTime
            self.fields.tested_at = currentTime
            self.fields.weeknum = int(currentTime.strftime("%W"))+1            
            if (self.fields.weeknum <=9):
                self.fields.image = "WW0"+str(self.fields.weeknum)+"-"+currentTime.strftime("%y")
            else:
                self.fields.image = "WW"+str(self.fields.weeknum)+"-"+currentTime.strftime("%y")
                
            return self.fields
    
    def set_results(self, results_file, suite):
        
        #take data from results file
        with open(results_file, 'rb') as csvfile:
            Features = Feature()
            Features.name = results_file.strip()
            results = csv.reader(csvfile, delimiter=',',quotechar="|")
            results.next()
            for row in results:
                Cases = Case()
                Cases.status = row[2]
                if (Cases.status == 'pass'):
                    self.fields.total_pass += 1
                    Features.total_pass += 1
                elif (Cases.status == 'fail'):
                    self.fields.total_fail += 1
                    Features.total_fail += 1
                Cases.comment = row[4]
                Cases.component = row[0]
                Cases.name = row[1]
                Cases.bug = row[3]
                Features.cases.append(Cases.__dict__)
                Features.total_cases += 1
            self.fields.total_cases = Features.total_cases
            self.fields.features = (Features.__dict__)
            self.fields.testtype = suite
        
        
    def upload_trc(self, results_file):
        #create an object to interact to the MongoDB
        url = self.url_target+self.auth_token
        url+= "\&release_version="+urllib.quote_plus(self.fields.release)
        url+= "\&target="+urllib.quote_plus(self.fields.profile)
        url+= "\&testtype="+urllib.quote_plus(self.fields.testtype)
        url+= "\&hwproduct="+urllib.quote_plus(self.fields.hardware )
        url+= "\&title="+urllib.quote_plus(self.fields.title)
        url+= "\&image="+urllib.quote_plus(self.fields.image)
        url+= "\&build_id="+urllib.quote_plus(self.fields.build_id)
        url+= "\&environment_txt="+urllib.quote_plus(self.fields.qa_summary_txt)
        url+= "\&qa_summary_txt=" + urllib.quote_plus(self.fields.qa_summary)  
        
        curl = 'curl -k --form report.1=@' + results_file +" "+ url  
        ###
        print "Creating the curl ...\n"
        print "Uploading " + results_file +" to TRC ...\n"
        mkoutput = DeviceInfo()
        mkoutput.get_output(curl)
        response = json.loads(mkoutput.out)
        #Error Handler
        if response["ok"] == "1":
            print "Success, you can view your report here : ", response["url"]
            return True;
        elif response["ok"] == "0":
            print "Error : ", mkoutput.out
            return False;
        else :
            print "Unhandle Error : ", mkoutput.out
            return False;
        
    def upload_db(self):
        print "Saving to MongoDB ..."
        mycon = Database()
        mydb = mycon.connect("GfxTestsBM")
        #Change to TestResults when is ready to production
        mydb.temp.save(self.fields.__dict__)
        print "----Completed----"
            
    def upload_default(self):
        reportIsUploaded = self.upload_trc(results_file)
        if(currentEnv == 'prod' and reportIsUploaded ):            
            self.upload_db()
            
    def offline_export(self):
        #save the curl to an output file
        t = datetime.today() 
        mytime = t.strftime('%Y%m%d_%H%M%S')            
        f = open("upload_"+mytime+".cfg", 'wb' )
        #Writing the cfg file
        f.write("[REPORT]\n")
        f.write("url_target: "+self.url_target+"\n")
        f.write("auth_token: "+self.auth_token+"\n")
        f.write("release_version: "+self.fields.release+"\n")
        f.write("target: "+self.fields.profile+"\n")
        f.write("testtype: "+self.fields.testtype+"\n")
        f.write("hwproduct: "+self.fields.hardware+"\n")
        f.write("title: "+self.fields.title+"\n")
        f.write("image: "+self.fields.image+"\n")
        f.write("build_id: "+self.fields.build_id+"\n")
        f.write("environment_txt: "+self.fields.qa_summary_txt+"\n")
        f.write("qa_summary_txt: "+self.fields.qa_summary+"\n")
        f.write("created_at: "+str(self.fields.created_at)+"\n")
        f.write("updated_at: "+str(self.fields.updated_at)+"\n")
        f.write("tested_at: "+str(self.fields.tested_at)+"\n")
        f.write("weeknum: "+str(self.fields.weeknum)+"\n")
        f.close()
        
        print "Output file "+ f.name+" was created"
        
        return f
    
    def offline_import(self, cfgfile, results_file):
        #Set the Parser
        config = ConfigParser.ConfigParser()
        config.read(cfgfile)
        config.get
        self.auth_token = config.get('REPORT', 'auth_token')
        self.url_target = config.get('REPORT', 'url_target')
        
        self.fields.release = config.get('REPORT', 'release_version')
        self.fields.profile = config.get('REPORT', 'target')
        self.fields.testtype = config.get('REPORT', 'testtype')
        self.fields.hardware = config.get('REPORT', 'hwproduct')
        self.fields.title = config.get('REPORT', 'title')
        self.fields.image = config.get('REPORT', 'image')
        self.fields.build_id = config.get('REPORT', 'build_id')
        self.fields.qa_summary_txt = config.get('REPORT', 'environment_txt')
        self.fields.qa_summary = config.get('REPORT', 'qa_summary_txt')
        self.fields.created_at = config.get('REPORT', 'created_at')
        self.fields.updated_at = config.get('REPORT', 'updated_at')
        self.fields.tested_at = config.get('REPORT', 'tested_at')
        self.fields.weeknum = config.get('REPORT','weeknum')
        
        url = self.url_target+"auth_token="+self.auth_token
        url+= "\&release_version="+urllib.quote_plus(self.fields.release)
        url+= "\&target="+urllib.quote_plus(self.fields.profile)
        url+= "\&testtype="+urllib.quote_plus(self.fields.testtype)
        url+= "\&hwproduct="+urllib.quote_plus(self.fields.hardware )
        url+= "\&title="+urllib.quote_plus(self.fields.title)
        url+= "\&image="+urllib.quote_plus(self.fields.image)
        url+= "\&build_id="+urllib.quote_plus(self.fields.build_id)
        url+= "\&environment_txt="+urllib.quote_plus(self.fields.qa_summary_txt)
        url+= "\&qa_summary_txt=" + urllib.quote_plus(self.fields.qa_summary)  
        
        #Call the set_results function
        self.set_results(results_file, self.fields.testtype)
        
        #Storing to MongoDB
        self.upload_db()
        
        #Making the post to TRC
        curl = 'curl -k --form report.1=@' + results_file +" "+ url  
        ###
        print "Creating the curl ...\n"
        print "Uploading " + results_file +" to TRC ...\n"
        mkoutput = DeviceInfo()
        mkoutput.get_output(curl)
        response = json.loads(mkoutput.out)
        #Error Handler
        if response["ok"] == "1":
            print "Success, you can view your report here : ", response["url"]
            return True;
        elif response["ok"] == "0":
            print "Error : ", mkoutput.out
            return False;
        else :
            print "Unhandle Error : ", mkoutput.out
            return False;        

class  Validator():
    def __init__(self):
        
        if currentEnv == "sand":
            self.platformList = ['BDW', 'BSW', 'BXT', 'BYT', 'HSW', 'ILK', 'IVB', 'KBL', 'SKL', 'SNB','NA']
            self.releaseList = ['Mesa Release', 'Platforms', 'Quarterly Release']
        else:
            self.platformList = ['BDW', 'BSW', 'BXT', 'BYT', 'HSW', 'ILK', 'IVB', 'KBL', 'SKL', 'SNB']
            self.releaseList = ['Installer', 'Kernel Release', 'Mesa Release', 'Platforms', 'Quarterly Release']
            
        self.suiteList = ['IGT', 'IGT kms-pipe-color', 'IGT psr', 'IGT basic', 'IGT core', 'IGT debugfs', 'IGT cursor',
                              'IGT drm', 'IGT drv', 'IGT fbc', 'IGT gem', 'IGT gen3', 'IGT gen7', 'IGT gpu_hang', 
                              'IGT hang', 'IGT kms', 'IGT kms-cursor', 'IGT kms-flip', 'IGT others', 'IGT pm', 'IGT power_mgmt',
                             'IGT prime', 'IGT psr', 'IGT sysfs', 'IGT fbc', 'IGT ctx',  'IGT dpms', 'IGT lpsp', 'IGT sprite_plane', 'PSR',
                             'CTS', 'Rendercheck', 'WebGLC', '3DGames', 'Apps','Piglit', 'DEQP', 'Reliability', 'Power', 'Stress', 'Suspend', 'Kernel', '2DManual',
                             'Media']
        
        self.platformList = sorted(self.platformList)
        self.releaseList = sorted(self.releaseList)
        self.suiteList = sorted(self.suiteList)

    def validateOpts(self, suite, release, platform, title, fileName):

        self.suiteValidation = False
        self.platformValidation = False
        self.releaseValidation = False
        self.titleValidation = False

        if not all((suite, release, platform, title, fileName)):
            if not suite:
                print "You must set an argument for the suite ex: -s 3DGames"
                self.suiteValidation = False
            if not release:
                print "You must set an argument for the release ex: -r 'Mesa Release'"
                self.releaseValidation = False
            if not platform:
                print "You must set an argument for the platform ex: -p SKL"
                self.platformValidation = False
            if not title:
                print "You must set an argument for the title ex: -t 2016-WW11"
                self.titleValidation = False
            if not fileName:
                print "You must set a results file to upload,  ex: -f 3DGames_Mesa_SKL_2016W11.csv"
                self.fileValidation = False
            
        else:
            
            self.suite = suite.strip()
            self.platform = platform.strip()
            self.release = release.strip()
            self.title = title.strip()
            self.titleValidation = True
            self.fileValidation = True

            for itemx, item in enumerate(self.suiteList):
                if self.suite.lower() == item.lower():
                    self.suiteValidation = True
                    self.suite= item
                    break;
                else:
                    if(itemx == len(self.suiteList)-1):
                        print ("%s is not a valid entry for a suite" % self.suite)  
                    
            for itemx, item in enumerate(self.platformList):
                if self.platform.lower() == item.lower():
                    self.platformValidation = True
                    self.platform = item
                    break;
                else:
                    if(itemx == len(self.platformList)-1):
                        print ("%s is not a valid entry for a platform" % self.platform)
            
            for itemx, item in enumerate(self.releaseList):
                if self.release.lower() == item.lower():
                    self.releaseValidation = True
                    self.release = item
                    break;
                else:
                    if(itemx == len(self.releaseList) -1):
                        print ("%s is not a valid entry for a release" % self.release)
            
        if (self.suiteValidation and self.platformValidation and self.releaseValidation and self.titleValidation):
            self.isValid = True  
        else:
            self.isValid = False
        
        return self
    
def main(argv=None):
    '''Command line options.'''
    program_name = os.path.basename(sys.argv[0])
    program_version = "v1.0"
    program_build_date = "%s" %datetime.today()

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
   
 
    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string)
        parser.add_option("-o", "--option", dest="option", default="ALL", help="Destiny where the information going to be uploaded ex: DB, TRC, ALL, OFFLINE", metavar="OPTION")
        parser.add_option("-f", "--file", dest="fileName", help="Name of the csv results file to be attached to the report", metavar="FILE")
        parser.add_option("-c", "--cfgfile", dest="cfgFile", default="NONE", help="Name of the config file exported offline", metavar="CFGFILE")
        parser.add_option("-s", "--suite", dest="suiteName", help="Suite that run on the test,  use '-d Suites' to view all the options", metavar="SUITE")
        parser.add_option("-p", "--platform", dest="platform", help="Platform type ex: HSW, BSW, SKL, BXT", metavar="PLATFORM")
        parser.add_option("-r", "--release", dest="release", help="Release name ex: Mesa Release, Platforms, Quaterly Release", metavar="RELEASE")
        parser.add_option("-t", "--title", dest="title", help="Main title for the report", metavar="TITLE")

        # process options

        (opts, args) = parser.parse_args(argv)     
        if hasattr(opts, 'option') and opts.option == "ALL":
            validator = Validator()
            validationResult = validator.validateOpts(opts.suiteName, opts.release, opts.platform, opts.title, opts.fileName)
            if (validationResult.isValid):
                print("Uploading results to TRC page & DataBase")
                upload_test = Uploader()
                upload_test.set_fields(opts.fileName, validationResult.release, validationResult.platform, validationResult.title, validationResult.suite)
                upload_test.upload_default(opts.fileName)
            else:
                print("Some of your arguments are not valid")
           
        elif hasattr(opts, 'option') and opts.option == "TRC":
            validator = Validator()
            validationResult = validator.validateOpts(opts.suiteName, opts.release, opts.platform, opts.title, opts.fileName)
            if (validationResult.isValid):
                print("Uploading results only to TRC page")
                upload_test = Uploader()
                upload_test.set_fields(opts.fileName, validationResult.release, validationResult.platform, validationResult.title, validationResult.suite)
                upload_test.upload_trc(opts.fileName)
            else:
                print("Some of your arguments are not valid")
                
        elif hasattr(opts, 'option') and opts.option == "DB": 
            validator = Validator()
            validationResult = validator.validateOpts(opts.suiteName, opts.release, opts.platform, opts.title, opts.fileName)
            if (validationResult.isValid):
                print("Uploading results only to DataBase")
                upload_test = Uploader()
                upload_test.set_fields(opts.fileName, validationResult.release, validationResult.platform, validationResult.title, validationResult.suite)
                upload_test.upload_db()
            else:
                print("Some of your arguments are not valid")
                
        elif hasattr(opts, 'option') and opts.option == "EXPORT":
            validator = Validator()
            validationResult = validator.validateOpts(opts.suiteName, opts.release, opts.platform, opts.title, opts.fileName)
            if (validationResult.isValid):
                print("Exporting results to output file")
                upload_test = Uploader()
                upload_test.set_fields(opts.fileName, validationResult.release, validationResult.platform, validationResult.title, validationResult.suite)
                upload_test.offline_export()
            else:
                print("Some of your arguments are not valid")
                
        elif hasattr(opts, 'option') and opts.option == "IMPORT":            
            print("Importing results from an offline export file")
            upload_test = Uploader()
            upload_test.offline_import(opts.cfgFile, opts.fileName)             
        # MAIN BODY #

    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":    
    #sys.argv.append()#("-l file.csv")
    main()
    sys.exit(0)
    sys.exit(main())
