from PyQt5.QtGui import QTextDocument, QPrinter, QApplication

import sys
app = QApplication(sys.argv)

doc = QTextDocument()
location = "c://apython//Jim//html//notes.html"
html = open(location).read()
doc.setHtml(html)

printer = QPrinter()
printer.setOutputFileName("foo.pdf")
printer.setOutputFormat(QPrinter.PdfFormat)
printer.setPageSize(QPrinter.A4);
printer.setPageMargins (15,15,15,15,QPrinter.Millimeter);

doc.print_(printer)
print ("done!")