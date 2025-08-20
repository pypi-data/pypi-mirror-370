## -*- coding: utf-8 -*-
from datetime import datetime
import pandas as pd
import os
import sys
try:
    from config import USER_EMAIL_GMAIL,USER_PASS_GMAIL,USER_CLB , PASS_CLB
except ImportError:
    USER_EMAIL_GMAIL = None
    USER_PASS_GMAIL = None
    USER_CLB = None
    PASS_CLB = None
    
if os.name=="nt":
    from win32com import client


import keyboard

import smtplib,ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders
import re
import time


def is_file_ready(filepath):
    """Verifica si el archivo está listo para ser usado."""
    try:
        with open(filepath, 'r+'):
            return True
    except IOError:
        return False


def print_there(x:int, y:int, text:str="")->None:
     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
     sys.stdout.flush()

def printxy(fila:int=10, columna:int=10, texto:str=""):
     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (fila, columna, texto))
     sys.stdout.flush()

def ClearCrt():
    """
    ClearCrt : Limp la pantalla de Consola símil a cls o Clear en otros idiomas.
    """
    if os.name in {"ce", "nt", "dos"}:
        os.system ("cls")
    else:
        os.system ("clear")
    return None

def CleanText(xTexto:str):
    """
    CleanText:
        Permite Eliminar caracteres especiales de un texto, como caracteres de control, colores, etc.

    Keyword arguments:
        xTexto: Texto con caracteres especiales o de control.
    return:
        Texto limpio sin caracteres de control.
    """
    # Lista de Códigos Scape y control a buscar y remplazar por nada.
    Secuencias_a_Remplazar_nada=[Color.ForeColor,
       Color.BackColor,
       Color.ForeColor256,
       Color.BackColor256,
       Color.Blanco,
       Color.LBlanco,
       Color.Rojo,
       Color.LRojo,
       Color.Verde,
       Color.LVerde,
       Color.Negro,
       Color.Amarillo,
       Color.LAmarillo,
       Color.Azul,
       Color.LAzul,
       Color.Cyan,
       Color.LCyan,
       Color.Bold,
       Color.Subrayado,
       Color.Invert,
       Color.Fin,
       Color.BRED,
       Color.BBLUE,
       "\x1b[1;36m",
       "\x1b[1;32m",
       "<br>",
       "</br>"]

    #for i in Secuencias_a_Remplazar_nada:
    #    xTexto=xTexto.replace(i,"")
    # Escapa las secuencias para regex y únelas con |
    patron = "|".join(re.escape(str(i)) for i in Secuencias_a_Remplazar_nada if i is not None)
    xTexto = re.sub(patron, "", xTexto)    
    return xTexto

class Color:
    ForeColor256 = "\x1b[38;5;"
    BackColor256 = "\x1b[48;5;"
    ForeColor = "\x1b[38;5;"
    BackColor = "\x1b[48;5;"
    Blanco    = "\x1b[37m"
    LBlanco   = "\x1b[97m"
    Rojo      = "\x1b[31m"
    LRojo     = "\x1b[91m"
    Verde     = "\x1b[32m"
    LVerde    = "\x1b[92m"
    Negro     = "\x1b[30m"
    Amarillo  = "\x1b[33m"
    LAmarillo = "\x1b[93m"
    Azul      = "\x1b[34m"
    LAzul     = "\x1b[94m"
    Bold      = "\x1b[1m"
    Subrayado = "\x1b[4m"
    Invert    = "\x1b[1;31;47m"
    Fin       = "\x1b[0m"
    # Colores en negrita (bold)
    BRojo  = "\x1b[1;31m"
    BVerde = "\x1b[1;32m"
    BAzul  = "\x1b[1;34m"
    #por compatibilidad con versiones anteriores
    BRED   = BRojo
    BGREEN = BVerde
    BBLUE  = BAzul
    Cyan    = "\x1b[36m"
    LCyan   = "\x1b[96m"
    BCyan   = "\x1b[1;36m"
    BCyan   = "\x1b[1;36m"

IsOK  = Color.Azul+"\u2611"+Color.Fin
IsBad = Color.Rojo+"\u2612"+Color.Fin

def cColor(texto:str="", color:str= Color.LAzul):
    return f"{color}{texto}{Color.Fin}"

def DiaSemana():
    Ahora = datetime.now()
    dias = {
    0: "Domingo",
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sábado"}
    return dias.get(int(Ahora.strftime("%w")))

_PRUEBA = True if not (DiaSemana() =="Martes" or DiaSemana()=="Lunes" )==-1 else False
_TIPOEJECUCION=Color.Bold+Color.Verde+("TEST" if _PRUEBA else "PRODUCTIVO")+Color.Fin

class logs:
    """ logs: Esta clase permite mantener un log de eventos qeu se muestran en pantalla y 
              se graban en un archivo de logs
        logs(NombreArchivo) --> NobreArchivo es el archivo donde se guardara el log.
        log.texto(xTexto)   -->

    """
    def __init__(self,NombreArchivo:str, xlog:bool=True):
        self.FileName=NombreArchivo
        self.ObjetoLogs=""
        self.ObjetoLogs=open(file=self.FileName, mode="w", encoding="utf-8")
        self.xlog = xlog

    def Texto(self, xTexto:str, clean_string:bool=True)->str:
        print(xTexto,end="")
        if self.xlog:
            # Primero limpia el texto de caracteres especiales
            xTexto=CleanText(xTexto) if clean_string else xTexto 
            self.ObjetoLogs.write(xTexto)

    def fin(self):
        self.ObjetoLogs.close()

    def Fin(self):
        self.ObjetoLogs.close()

class ProgressBar:
    def __init__(self,x,y,Total=None):
        self.x=x
        self.y=y
        self.Inicio=True
        self.Ancho=40
        self.Mensaje=""
        self.Total=100 if Total==None else Total

    def Box(self,Texto=""):
        self.Mensaje=Texto
        self.Ancho=len(CleanText(self.Mensaje))
        print_there(self.x  ,self.y ,Color.ForeColor+Color.LAzul+'╭'+'─'*self.Ancho+'╮'+Color.Fin)
        print_there(self.x+1,self.y ,Color.ForeColor+Color.LAzul+'│'+Color.ForeColor+Color.LAmarillo+self.Mensaje.center(self.Ancho," ")+Color.ForeColor+Color.LAzul+'│'+Color.Fin)
        print_there(self.x+2,self.y ,Color.ForeColor+Color.LAzul+'│'+Color.ForeColor+Color.LAmarillo+self.Ancho*" "+Color.ForeColor+Color.LAzul+'│'+Color.Fin)
        print_there(self.x+3,self.y ,Color.ForeColor+Color.LAzul+'╰'+'─'*self.Ancho+'╯'+Color.Fin)

    def Avance(self,Valor=0):
        Valor=round(Valor)
        xDelta=0 if len(self.Mensaje)==0 else 2

        if self.Inicio:
            self.Inicio=False
            print_there(self.x+xDelta,self.y+1,Color.ForeColor+Color.LBlanco+"├"+"─"*(self.Ancho-6)+"┤"+Color.Fin)

        if Valor>=0 and Valor<=100:
            xAvance=round((self.Ancho-6)*Valor/100)
            print_there(self.x+xDelta,self.y+2, Color.ForeColor+Color.LVerde+"■"*xAvance+Color.Fin)
            print_there(self.x+xDelta,self.y+round(self.Ancho-3),f"{Color.ForeColor+Color.Rojo}{Valor}%"+Color.Fin)

    def __str__(self):
        return  f"\n\npos({self.x},{self.y}) | Mensaje: {self.Mensaje} | Ancho: {self.Ancho }"

class Table:
    def __init__(self,xDF,xTipo=0) -> None:
        self.xDataFrame=xDF
        self.xTipo=xTipo
        self.xBox=[["╭","─","┬","╮","│","├","┼","┤","╰","┴","╯"],
                   ["+","-","+","+","|","+","+","+","+","+","+"],
                   ["╔","═","╦","╗","║","╠","╬","╣","╚","╩","╝"]]
        self.xSalida=""
        self.LineaFinal=""

    def Head(self):
        Linea1,Linea2,Linea3,Linea4="","","",""
        Linea1=self.xBox[self.xTipo][0] #  ╭
        Linea2=self.xBox[self.xTipo][4] #  │
        Linea3=self.xBox[self.xTipo][5] #  ├
        Linea4=self.xBox[self.xTipo][8]
        Lista=list(self.xDataFrame.columns)
        for x in range(len(self.xDataFrame.columns)):
            Linea1+=self.xLargo(self.xDataFrame,Lista[x])*self.xBox[self.xTipo][1]
            Linea2+=Lista[x].center(self.xLargo(self.xDataFrame,Lista[x])," ")
            Linea3+=self.xLargo(self.xDataFrame,Lista[x])*self.xBox[self.xTipo][1]
            Linea4+=self.xLargo(self.xDataFrame,Lista[x])*self.xBox[self.xTipo][1]
            if x==len(Lista)-1:
                Linea1+=self.xBox[self.xTipo][ 3]+"\n"
                Linea2+=self.xBox[self.xTipo][ 4]+"\n"
                Linea3+=self.xBox[self.xTipo][ 7]+""
                Linea4+=self.xBox[self.xTipo][10]+""
            else:
                Linea1+=self.xBox[self.xTipo][2]
                Linea2+=self.xBox[self.xTipo][4]
                Linea3+=self.xBox[self.xTipo][6]
                Linea4+=self.xBox[self.xTipo][9]

        self.xSalida+=Linea1
        self.xSalida+=Linea2
        self.xSalida+=Linea3
        self.LineaFinal=Linea4
        return self.xSalida

    def xLargo2(self,xDF,xCol):
        MiMax=-1e100
        MiMax=len(xCol)
        MiLargo=0
        for x in range(len(xDF[xCol])):
            if xDF[xCol].dtype == object and isinstance(xDF.iloc[0][xCol], str):
                MiLargo=len(xDF[xCol][x])
                MiMax=MiLargo if MiLargo>MiMax else MiMax
        return MiMax

    # Borrar xLargo2
    def xLargo(self,xDF,xCol):
        MiMax = -1e100
        MiMax = len(xCol)
        xMiLargo = 10
        for x in range(len(xDF[xCol])):
            if xDF[xCol].dtype == object and xDF.iloc[x][xCol] is None:
                xMiLargo = 4

            elif xDF[xCol].dtype == object and isinstance(xDF.iloc[x][xCol], float):
                #xMiLargo=len(xDF[xCol][x])
                xMiLargo = len(str(xDF.iloc[x][xCol]))

            elif xDF[xCol].dtype == object and isinstance(xDF.iloc[x][xCol], str):
                #xMiLargo=len(xDF[xCol][x])
                xMiLargo = len(xDF.iloc[x][xCol])

            elif xDF[xCol].dtype == object and isinstance(xDF.iloc[x][xCol],datetime):
                xMiLargo = len(xDF[xCol][x].strftime('%Y-%m-%d'))
            if (xMiLargo > MiMax):
                MiMax = xMiLargo  #else MiMax

        return MiMax

    def footer(self):
        #print(self.LineaFinal)
        #self.xSalida+=self.LineaFinal
        return self.LineaFinal

    def Body(self):
        Lista=list(self.xDataFrame.columns)
        #df=self.xDataFrame
        LineaBody=""
        ### Recorre el data frame por Fila
        for i in range(len(self.xDataFrame)):
            LineaBody+=self.xBox[self.xTipo][4]
            for x in range(len(self.xDataFrame.columns)):
                if str(type(self.xDataFrame[Lista[x]][i]))=="<class 'numpy.int64'>":
                    xAncho=len(str(self.xDataFrame[Lista[x]][i]))
                    xColAncho=len(Lista[x])

                    xFill=xAncho if xAncho>xColAncho else xColAncho
                    xCadena=f"{self.xDataFrame[Lista[x]][i]}"
                    xCadena=abs(xFill-len(xCadena))*" "+xCadena
                    LineaBody+=xCadena
                    #.center(," ")

                if  str(type(self.xDataFrame[Lista[x]][i]))=="<class 'numpy.bool_'>":
                    xAncho=self.xLargo(self.xDataFrame,Lista[x])
                    LineaBody+=f"{self.xDataFrame[Lista[x]][i]}".center(xAncho," ")

                if str(type(self.xDataFrame[Lista[x]][i]))=="<class 'str'>":
                    xAncho=len(str(self.xDataFrame[Lista[x]][i]))
                    xColAncho=len(Lista[x])
                    xAncho=self.xLargo(self.xDataFrame,Lista[x])
                    xFill=xAncho if xAncho>xColAncho else xColAncho
                    xCadena=f"{self.xDataFrame[Lista[x]][i]}"
                    xCadena=xCadena+abs(xFill-len(xCadena))*" "
                    LineaBody+=xCadena

                LineaBody+=self.xBox[self.xTipo][4]

            if i<len(self.xDataFrame)-1:
                LineaBody+="\n"
        return LineaBody

    def View(self) -> str:
        Final=self.Head()+"\n"+self.Body()+"\n"+self.footer()
        return Final #self.xSalida

def PrintError(e,connextion=""):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(f"\n\nError en Linea : {Color.Rojo}{exc_tb.tb_lineno}{Color.Fin} en {Color.Rojo}{fName}{Color.Fin}")
    print(exc_type)
    print(f"Error Inesperado: {Color.Rojo}{str(sys.exc_info()[0])}")
    print(str(e))
    print(str(EnvironmentError)+Color.ENDC)
    #print(Color.FAIL+"No se puede conectar a la base de datos"+Color.ENDC)
    if not connextion=="":
        connextion.close()

class Cronometro:
    """
    Cronometro: Temporizador
    """
    def __init__(self):
        self.Iniciar=datetime.now()
        self.Actual=0
        self.DeltaTiempo=0
        #self.Ahora=self.Iniciar

    def Delta(self):
        self.Actual=datetime.now()
        self.DeltaTiempo=self.Actual-self.Iniciar
        #return f"{self.DeltaTiempo: %H:%M:%S}"
        return self.DeltaTiempo

    def Reset(self):
        self.Iniciar=datetime.now()

    def Termino(self):
        return f"[ {self.Delta()} ]  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

    def now(self):
        return datetime.now()

    def Ahora(self):
        return datetime.now()

    def Inicio(self):
        return f"{self.Iniciar::%d/%m/%y %H:%M:%S}"

    def Año(self):
        return self.Iniciar.year

    def Mes(self):
        return self.Iniciar.month

    def Dia(self):
        return self.Iniciar.day

    def __str__(self):
        #return f"Delta Time {self.Iniciar}"   #=datetime.now()
        return f"{self.Iniciar::%d/%m/%y %H:%M:%S}"

def ImportarHojasXLSX(Ruta,Archivo,Hoja,Encabezados=0,AgregaOrigen=True,Mensajes=False):
    """
    ImportarHojasXLSX: Permite importar Hojas de Calculo en Pandas.\n
        Ruta        : Ruta de Archivo Excel a Importar.
        Archivo     : Excel del que se importara la hoja.
        Hoja        : Hoja de la que se extraeran los datos.
        Encabezados : Fila donde están los encabezados, Cero sin encabezados.
        AgregaOrigen: Agrega dos columnas con información desde donde se obtuvieron los datos.
    \n
                Retorna un DataFrame.
    """
    Ahora=Cronometro()
    if Mensajes:
        print(f"Lectura de Archivo Excel {Color.BBLUE}{Archivo}{Color.ENDC}\nHoja {Color.BBLUE}{Hoja}{Color.ENDC}",end="\t- ")
    df = pd.read_excel(Ruta+"/"+Archivo, sheet_name=Hoja,header=Encabezados,engine='openpyxl')
    if AgregaOrigen:
        df['Archivo']=Archivo
        df['Hoja']=Hoja
        if Mensajes:
            print(f"N° Filas Filtradas :{len(df)}\tDelta: {Ahora.Delta()}")
    return df

if os.name=="nt":
    def EnviarCorreoAdjunto(destinatario='lcorales', Titulo="@Python - Correos Automáticos", copy=None, mensaje=None, adjunto=None, html=False):
        #### NOTA:
        ####      Recordar que tanto los destinatarios como los en copia se separan con ;
        ####      Este proceso funciona sin problemas para enviar desde Outlook sin pasar credenciales (talvez solo si esta uno logeado)
        olook = client.Dispatch("Outlook.Application")
        mail = olook.CreateItem(0)
        mail.To = destinatario
        mail.Subject = Titulo
        mail.Importance= 2

        if not copy is None:
            mail.CC = copy

        if html:
            if not mensaje is None:
                mail.HTMLBody = mensaje
        else:
            if not mensaje is None:
                mail.Body = mensaje

        if not adjunto is None:
            mail.Attachments.Add(adjunto)

        mail.Send()

def emailSender(xTo ,Asunto="TEST", xBody="Hola Mundo",xServer="Outlook",adjunto=""):
    """
    emailSender : Permite enviar correos con adjuntos si se requiere.
    @parameters :
        xTo     : Destinatario(s), si es mas de uno se debe separar con ';'
        Asunto  : Texto del Asunto o referencia del mensaje.
        xBody   : Texto del cuerpo principal del Mensaje, texto plano o HTML
        xServer : Servicio de correo que se utilizara, ya sea "Outlook" o "gmail"
        adjunto : Archivo en cualquier formato que se enviara como adjunto.
    """
    xTo=xTo.split(";")
    for addr_to in xTo:
        addr_from  = USER_EMAIL_GMAIL  if xServer=="gmail" else USER_CLB
        smtp_server='smtp.gmail.com'   if xServer=="gmail" else 'smtp-mail.outlook.com' 
        #'smtp.office365.com' # #'smtp.office365.com' # # #'smtp-mail.outlook.com'
        
        smtp_port   = 587  #25

        smtp_user   = USER_EMAIL_GMAIL if xServer=="gmail" else USER_CLB
        smtp_pass   = USER_PASS_GMAIL  if xServer=="gmail" else PASS_CLB

        # Construct email
        msg = MIMEMultipart('alternative')
        msg['To'] = addr_to
        msg['From'] = addr_from
        msg['Subject'] = Asunto

        # Record the MIME types of both parts - text/plain and text/html.
        #part1 = MIMEText(text, 'plain')
        part2 = MIMEText(xBody, 'html')
        if not adjunto=="":
            xFile1 = MIMEBase('application', "octet-stream")
    
            xFile1.set_payload(open(adjunto, "rb").read())
            encoders.encode_base64(xFile1)
            xFile=os.path.basename(adjunto)
            xFile1.add_header('Content-Disposition', f"attachment; filename={xFile}")
            msg.attach(xFile1)

        msg.attach(part2)

        # Send the message via an SMTP server
        try:

            s = smtplib.SMTP(host=smtp_server, port=smtp_port)

            # only TLSv1 or higher
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3

            s.ehlo()
            if s.starttls(context=context)[0] != 220:
                return False # cancel if connection is not encrypted
            s.ehlo()
            s.login(smtp_user,smtp_pass)
            s.sendmail(addr_from, addr_to, msg.as_string())
            s.quit()

        except Exception as e:
            print("Error Inesperado: ", sys.exc_info()[0])
            print(e)
            print(EnvironmentError)
            print("ERROR ----> Se produjo un Error al tratar de enviar el correo, cheque, la configuración smtp.")
            ErroresCorreos=1

def Box(Texto=""):
    xAncho=len(CleanText( Texto))
    print(Color.ForeColor256+Color.Azul+'╭'+'─'*xAncho+'╮'+Color.Fin)
    print(Color.ForeColor256+Color.Azul+'│'+Color.Fin+Color.ForeColor256+Color.Blanco+Color.Bold+Texto.center(xAncho," ")+Color.Fin+Color.ForeColor256+Color.Azul+'│'+Color.Fin)
    print(Color.ForeColor256+Color.Azul+'╰'+'─'*xAncho+'╯'+Color.Fin)
    return None

def toVars(xNumero):
    """
    toVars  : Permite crear cadena de sustitución para consultas SQL con %s\n
    xNumero : Cantidad de %s que se crearan.
    """
    xPassVariables="%s,"*xNumero
    xPassVariables=xPassVariables[:-1]
    return xPassVariables

def GenerateQuery(xdf,TABLENAME,Tipo="REPLACE"):
    """
    GenerateQuery() -> Permite Generar la Clausula Query\n
    xdf             -> DataFrame que se usara\n
    Tipo            -> Puede ser Insert o Replace
    """
    Mis_Campos=df2colstr(xdf) # Obtiene un String con las columnas de la Tabla
    xPassVariables=toVars(len(xdf.columns)) # crea la cadena %s de remplazo según la cantidad de campos
    Consulta=f"{Tipo.upper()} INTO {TABLENAME}({Mis_Campos}) VALUES ({xPassVariables});"
    return Consulta

def MessageBox(Texto="Falta el Mensaje", opciones="SN"):
    """
    Requisito previo : pip install keyboard
    MessageBox -> Muestra un mensaje en la pantalla y espera a que se presionen algunas de las 
        teclas indicadas.\n
        Texto    : Mensaje a desplegar\n
        Opciones : las teclas que se espera que presionen
    """
    xTeclas=list(opciones)
    xkey=""
    for xOpcion in xTeclas:

        xkey+=f"{Color.ForeColor256+Color.Rojo} {xOpcion} {Color.Fin} / "
    xkey=xkey[:-2]
    print(f"\n{Color.ForeColor256+Color.Verde}{Texto}{Color.Fin}  {xkey}\n")
    # Espera hasta que se presione unas de las teclas indicado en Opciones, da lo mismo 
    # si es mayúscula o minúscula
    while True:
        tecla=keyboard.read_key().upper()
        if tecla in opciones:
            break
    return tecla