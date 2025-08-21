# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility.
 
@note: Translate selected Confluence wiki pages to GitLab flavored markdown.
Created on 04.08.2024   

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake
       - HTML2Text
       - atlassian
   
@author: garb_ma                                                                         [DLR-SY,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
from PyXMake.Tools import Utility
from PyXMake.Build.Make import AllowDefaultMakeOption, Custom

import os, sys
import re, copy
import argparse
import html2text

from bs4 import BeautifulSoup

try: from dlrwiki import DLRWiki as Base
except ImportError: from atlassian import Confluence as Base

class Confluence(Base,Custom):
    """
    Build class to export Wiki pages from Confluence to GitLab flavored Markdown.
    
    @note: Can be accessed as a pure base class alike
    """        
    # Definition of class attribute
    base_url = os.getenv("pyx_confluence_url","https://wiki.dlr.de/")
    
    def __init__(self, *args, **kwargs):
        """
        Initialization of Confluence class object.
        """
        # Use atlassian API class as primary base      
        super(Confluence, self).__init__(url=kwargs.pop("base_url",kwargs.pop("url",self.base_url)),**kwargs)
        ## String identifier of current instance.                
        self.MakeObjectKind = "Confluence"
        
        # Default line break operator
        linebreak = "\n"
        
        # Accept both space and tile as well as page id
        if not str(args[0]).isdigit(): self.buildid = self.get_page_id(*args)
        else: self.buildid = int(args[0])

        # We now have one page id
        page_id = self.buildid
        
        # Get data directly from confluence
        page_data = { x.split(".")[-1]: self.get_page_by_id(page_id, expand=x) for x in ["body.view","body.storage"] }
        
        # Get title and data in HTML or CSF format respectively
        page_title = page_data["view"]["title"]
        page_html = page_data["view"]['body']["view"]["value"]
        page_storage = page_data["storage"]['body']["storage"]["value"]
        
        # Enforce naming convention
        page_title = page_title.replace("-",""); 
        page_title = str("".join([x for x in page_title if not x.isdigit()]).strip())
        page_title_seperator = "-" if not "-" in page_title else "_"

        # Use BeautifulSoup to extract raw text from HTML
        soup = BeautifulSoup(page_storage, 'html.parser')
        page_text = [x.strip() for x in soup.get_text("!$$$#").split("!$$$#")]

        # Use HTML2Text to preselect some types
        h = html2text.HTML2Text(); h.ignore_links = False; h.mark_code = True

        # Get sanitized raw data by comparing soup HTML output with HTML2Text feature
        markdown_text = [x.strip() for x in h.handle(page_html).split(linebreak) if Utility.IsNotEmpty(x)]
        page_text = list(Utility.ArbitraryFlattening([x.split(linebreak) for x in page_text if any(y in x for y in markdown_text)]))

        # Collect all headers. Add anchor support by default
        page_headers = {}        
        for _, block in enumerate(markdown_text): 
            if block.startswith("#"): 
                header = block.split("#")[-1] ; anchor = re.sub('([()#])',"", block)
                if not "(#" in block: page_headers.update({header:block[:block.rfind('#')+1]+" [%s](#%s)" % (header.strip(), anchor.strip())})
                page_text = [page_headers[header] if header in x else x for x in page_text]
                
        # Store all relevant data for later use as class attributes
        self.page_id = page_id
        self.page_title = page_title
        self.markdown_text = copy.deepcopy(markdown_text)
        self.raw_text = copy.deepcopy(page_text)
        
        # This is the output file name of a single run
        self.markdown_file = "%s.md" % page_title.replace(" ",page_title_seperator)
        pass
    
    def OutputPath(self, path, **kwargs):
        """
        Define a new output directory. Output is written to the workspace by default.
        
        @note: If output directory does not exists, create one in the process
        """
        # Modify inherited class method
        self.copyfiles = getattr(self, "copyfiles",[])
        if not os.path.exists(path): os.makedirs(path, exist_ok=True)
        # Call overwritten class method afterwards
        Custom.OutputPath(self, path, files=kwargs.get("files",""))
        pass
        
    def create(self, *args, **kwargs): 
        """
        Execute make command
        """
        linebreak = "\n"
        
        # Variable initialization
        start = 0; collect = 0
        block = ""; image = False; expand = False
        markdown_flavored_text = []
        
        ## Add page title to the top of the markdown file. Defaults to False.
        # GitLab wiki flavored markdown automatically display the page name on top
        if kwargs.get("add_page_title",False): markdown_flavored_text.append("# [%s](#%s)" % (str(self.page_title),str(self.page_title)))
        
        # Operate fully in the output directory
        with Utility.ChangedWorkingDirectory(self.outdir):
            ## Loop over all text lines from the WIKI.
            # Discard duplicates and recover block, code and image attachments
            for _, line in enumerate(self.raw_text):
                # In case of segmented statements
                collect = max(0,collect -1)
                ## Code block check
                # Collect all code blocks and remove unsupported headers. 
                # Deal with multi-line statements
                try: 
                    start = self.markdown_text.index(line,start) -1
                    # All code blocks should start with [code]
                    if self.markdown_text[start] in ["[code]"]:
                        end = self.markdown_text.index("[/code]",start) +1
                        line = linebreak.join(
                                   self.markdown_text[start:end]).replace("[code]",r"```").replace("[/code]",r"```")
                        del self.markdown_text[start:end]
                        if self.markdown_text[start-1] == str("**%s**" % markdown_flavored_text[-1]): 
                            markdown_flavored_text.pop(-1)
                except ValueError: pass
                finally: pass
                ## Notification block
                # Customized quote for warning and or notifications
                if block:
                    line = block + "%s\n" % line; 
                    if collect <= 0: block = ""
                ## Image block
                # Collect all images and rewrite the source URL dynamically
                if image:
                    match = re.search( r'src="([^"]+)"', line)
                    if match:
                        fname = Utility.PathLeaf(match.group(1))
                        attachments = self.get_attachments_from_content(self.page_id, filename=fname)['results']
                        for attachment in attachments:
                                r = self._session.get(self.url + attachment['_links']['download'])
                                if r.status_code == 200:
                                    with open(fname, "wb") as f:
                                        for bits in r.iter_content(): f.write(bits)
                        line = line.replace(match.group(1),fname) + "\n"
                        image = False
                ## Expand block
                # Collect all images and rewrite the source URL dynamically
                if expand:
                    if collect <= 0:
                        line = line +"\n</details>\n"
                        expand = False
                    else: line = line + "\n"
                ## Special block check
                # Collect all special purpose blocks. Supports custom headers
                # Used to translate special block structures like notes and warnings. Requires prior markdown notification
                if line.startswith("<!-- pyxmake-flavored-markdown"): 
                    selector = str(line.split(":")[-1].split("--")[0]).strip()
                    # Multiple lines statements
                    if "collect" in selector: 
                        collect = int(selector.split("=")[-1].split("-")[0])
                    # Block quote section
                    if "block" in selector: 
                        block = "> "
                        if selector.endswith("header"): 
                            if not selector.startswith("block"): emoji = ":%s: " %selector.split("-")[0]
                            markdown_flavored_text[-1] = block+emoji+ "**%s**  " % markdown_flavored_text[-1]
                            del emoji
                    # Details section
                    if "expand" in selector: 
                        expand = True
                        if selector.endswith("header"): 
                            markdown_flavored_text[-1] = "<details><summary>%s</summary>" % markdown_flavored_text[-1]
                    # Image section
                    if "image" in selector: image = True
                    continue
                try: 
                    if re.sub(r'[^\w]', '', line) in re.sub(r'[^\w]', '', markdown_flavored_text[-1]): continue
                except IndexError: pass           
                markdown_flavored_text.append(line)
    
            with open(self.markdown_file, 'w') as f:
                for line in markdown_flavored_text: f.write("%s\n" % line)
            pass
        
    @classmethod
    def parse(cls, **kwargs): # pragma: no cover
        """
        Execute the current class as a CLI command.
        """
        # Evaluate current command line
        command = kwargs.pop("command",sys.argv)
        # Process all known arguments        
        parser = argparse.ArgumentParser(description="Translate a confluence wiki page to GitLab flavoured markdown.", parents=[Confluence.__parser__()])
        # Remove all unsupported command line arguments
        Utility.RemoveArguments(parser,  ["name","source","include","scratch","verbosity"])
        parser.add_argument('source', type=str, nargs=1, help="A confluence wiki space  or page id. If a wiki space is given, a list of files must be given.")
        parser.add_argument("-t","--token", type=str, help="Token for the Atlassian Confluence Wiki instance. Mandatory.")
        parser.add_argument("-u","--url", type=str, help="URL to an Atlassian Confluence Wiki instance. Defaults to DLR infrastructure.")
        parser.add_argument("--incremental", type=Utility.GetBoolean, const=True, default=False, nargs='?', 
            help="Toggle between incremental and non-incremental build. When activated, source is treated as parent from which all child pages are translated. Defaults to False.")
        # Check all options or run unit tests in default mode
        try:
            # Check CLI options
            _ = command[1]
            args, _ = parser.parse_known_args(command[1:])
            # Specification of source space is mandatory
            source = Confluence.sanitize(args.source[0]); 
            # Optional non-default definition to add files
            try: 
                _ = getattr(args,"files")
                # Sanitize the given file names
                files = [Confluence.sanitize(x) for x in Utility.ArbitraryFlattening(getattr(args,"files"))]
            except: files = []
            # Optional non-default output directory
            try: output = args.output[0]
            except: output = os.getcwd()
            # Create a dictionary combining all settings
            settings = {"files":files, "output":output}
            # Update API. Defaults to environment variable settings, which defaults to DLR instance.
            if getattr(args,"url",None): settings.update({"base_url":getattr(args, "url")})
            # Token and incremental setting must be/are always given
            for key in ["token","incremental"]: 
                if getattr(args,key): settings.update({key:getattr(args,key)})
        # Use an exception to allow help message to be printed.
        except Exception as _:
            # Run default test coverage of all integrated projects.
            if AllowDefaultMakeOption:                       
                cls.call("SY", "1 - System requirements and installation", **kwargs)
        else:
            # Execute valid CLI command
            cls.call(source, **settings)
        pass

    @staticmethod
    def call(*args,
        # Default output directory
        output=os.getcwd(),
        # Additional keyword arguments
        **kwargs):
        """
        Assemble all settings for a class call
        """
        # Collect all files by means of child pages or directly given
        incremental = kwargs.pop("incremental",False)
        ListofFiles = kwargs.pop("files",[])
        if incremental and not ListofFiles:
            confluence = Confluence(*args, **kwargs)
            ListofFiles = confluence.get_child_id_list(confluence.page_id)
        # Execute command 
        for idf, file in enumerate(ListofFiles,1):
            # Create a new instance
            if not incremental: confluence = Confluence(*args, file, **kwargs)
            else: confluence = Confluence(file, **kwargs)
            # Set a user-defined output directory. Defaults to the current working directory
            confluence.OutputPath(output)
            # Execute the process
            confluence.create()
            # Do not process parent page
            if idf == len(ListofFiles): break
        else:
            # Create a new instance
            confluence = Confluence(*args, **kwargs)
            # Set a user-defined output directory. Defaults to the current working directory
            confluence.OutputPath(output)
            # Execute the process
            confluence.create()
        pass
        
def main(*args, **kwargs):
    """
    Main function to execute the script.
    """
    # Execute this class as a function
    Confluence.call(*args, **kwargs)
    pass

if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    Confluence.run()
    # Finish
    print("==================================")    
    print("Finished")
    print("==================================")    
    sys.exit()