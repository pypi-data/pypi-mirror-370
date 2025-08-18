#load packages
import saspy, sys, re, requests, warnings
from IPython.core.magic import register_cell_magic
from IPython.display import HTML
from saspy.SASLogLexer import SASLogStyle, SASLogLexer
from saspy.sasbase import SASsession
from pygments.formatters import HtmlFormatter
from pygments import highlight

#surpress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", category=ImportWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

#jar files 
version=str(sys.version_info.major)+'.'+str(sys.version_info.minor)
url = 'https://www.googleapis.com/drive/v3/files/1wQkHbgrcF03hN8CrIFLK4zsqU-ckVRyK?alt=media&key=AIzaSyBfJIzuu9x7AZjgtr0UhbrxNTz0vqbYWv0'
dst = '/usr/local/lib/python'+version+'/dist-packages/saspy/java/iomclient/sas.rutil.jar'
open(dst, 'wb').write(requests.get(url).content)
url = 'https://www.googleapis.com/drive/v3/files/1wUiEDOu2UMsW6394MrC0s4D-FHPAlt8o?alt=media&key=AIzaSyBfJIzuu9x7AZjgtr0UhbrxNTz0vqbYWv0'
dst = '/usr/local/lib/python'+version+'/dist-packages/saspy/java/iomclient/sas.rutil.nls.jar'
open(dst, 'wb').write(requests.get(url).content)
url = 'https://www.googleapis.com/drive/v3/files/1wTOLejKU5UKw61KGu4oT_WM4ZdWOAdqu?alt=media&key=AIzaSyBfJIzuu9x7AZjgtr0UhbrxNTz0vqbYWv0'
dst = '/usr/local/lib/python'+version+'/dist-packages/saspy/java/iomclient/sastpj.rutil.jar'
open(dst, 'wb').write(requests.get(url).content)

#define log-in module
def SASLogin(id, pw):
    def SASMagic(sas) : 
      sas.submit("""
      proc template;
        define style Styles.Hangul;
        parent = Styles.HTMLBlue;
        style graphfonts from graphfonts /
              'NodeDetailFont' = ("Gulim",7pt)
              'NodeInputLabelFont' = ("Gulim",9pt)
              'NodeLabelFont' = ("Gulim",9pt)
              'NodeTitleFont' = ("Gulim",9pt)
              'GraphDataFont' = ("Gulim",7pt)
              'GraphUnicodeFont' = ("Gulim",9pt)
              'GraphValueFont' = ("Gulim",9pt)
              'GraphLabel2Font' = ("Gulim",10pt)
              'GraphLabelFont' = ("Gulim",10pt)
              'GraphFootnoteFont' = ("Gulim",10pt)
              'GraphTitleFont' = ("Gulim",11pt,bold)
              'GraphTitle1Font' = ("Gulim",14pt,bold)
              'GraphAnnoFont' = ("Gulim",10pt);         
        end;
      run;
      """)
      sas.HTML_Style = "Hangul"
      sas.submit("""
      OPTIONS VALIDVARNAME=ANY;
      
      filename kosis "/home/&sysuserid/sasuser.v94/macro.sas";
      PROC HTTP URL="https://www.googleapis.com/drive/v3/files/1O-cblV3r1iYckJNQttOkFZVXGLJi8pkz?alt=media&key=AIzaSyBfJIzuu9x7AZjgtr0UhbrxNTz0vqbYWv0" METHOD='GET' OUT=KOSIS;
      
      %INCLUDE "/home/&sysuserid/sasuser.v94/macro.sas";
      %SYMDEL TEMP;
                    
      %LET MARKER=MARKERS MARKERATTRS=(SYMBOL=CIRCLEFILLED SIZE=11); 
      %LET DATALABEL=DATALABEL DATALABELATTRS=(SIZE=11); 
      %LET PRINTIT=%STR(PROC PRINT DATA=RAW(OBS=3);RUN;); 
      %LET XAXIS=XAXIS TYPE=DISCRETE VALUEATTRS=(SIZE=10.5) LABELATTRS=(SIZE=10.5) DISPLAY=(NOLABEL); 
      %LET YAXIS=YAXIS GRID VALUEATTRS=(SIZE=10.5) LABELATTRS=(SIZE=10.5) LABELPOS=TOP;
      
      ODS GRAPHICS/IMAGEMAP;

      """)
      print("알림 : KOSIS_MACRO_V3_5, ECOS2, ECOS3, ENARA, POSTDATA, LOCALFINANCE 매크로를 로드하였습니다.")
      print("알림 : 매크로 변수 MARKER, DATALABEL, PRINTIT, XAXIS, YAXIS를 로드하였습니다.")
      print("알림 : ODS GRAPHICS IMAGEMAP 옵션을 로드하였습니다.")
      print("알림 : Jupyter Notebook Cell Magic %%SASK를 로드하였습니다.")
              
      def _which_display(sas, log, output):
        lst_len = 30762
        lines = re.split(r'[\n]\s*', log)
        i = 0
        elog = []
        for line in lines:
            i += 1
            e = []
            if line[sas.logoffset:].startswith('ERROR'):
                e = lines[(max(i - 15, 0)):(min(i + 16, len(lines)))]
            elog = elog + e
        if len(elog) == 0 and len(output) > lst_len:   # no error and LST output
            return HTML(output)
        elif len(elog) == 0 and len(output) <= lst_len:   # no error and no LST
            color_log = highlight(log, SASLogLexer(), HtmlFormatter(full=True, style=SASLogStyle, lineseparator="<br>"))
            return HTML(color_log)
        elif len(elog) > 0 and len(output) <= lst_len:   # error and no LST
            color_log = highlight(log, SASLogLexer(), HtmlFormatter(full=True, style=SASLogStyle, lineseparator="<br>"))
            return HTML(color_log)
        else:
            color_log = highlight(log, SASLogLexer(), HtmlFormatter(full=True, style=SASLogStyle, lineseparator="<br>"))
            return HTML(color_log + output)

      @register_cell_magic
      def SASK(line, cell):
          sas.submit("proc optsave out=__jupyterSASKernel__; run;")
          if len(line) > 0 :
              res = sas.submit("ods layout gridded columns=" + str(line) + " advance=table;" + cell + "ods layout end;")
          else :
              res = sas.submit(cell)        
          dis = _which_display(sas, res['LOG'], res['LST'])
          sas.submit("proc optload data=__jupyterSASKernel__; run;")
          return dis
   

    sas = saspy.SASsession(
                java='/usr/bin/java',
                iomhost=['odaws01-apse1.oda.sas.com', 'odaws01-apse1-2.oda.sas.com', 'odaws01-usw2.oda.sas.com', 'odaws01-usw2-2.oda.sas.com', 'odaws01-euw1.oda.sas.com'],
                iomport=8591,
                encoding='utf-8',
                omruser=str(id),
                omrpw=str(pw)
            )
    SASMagic(sas)                
    
    return sas

