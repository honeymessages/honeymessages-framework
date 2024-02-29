#!/usr/bin/python3

# 2020/03/27
# make-pdf-phone-home, use it to create a PDF document that automatically sends requests to a url when the document is
# opened
# requires module mPDF.py by Didier Stevens who thankfully put his code in public domain.
# Source code put in public domain by Didier Stevens, no Copyright https://DidierStevens.com. Use at your own risk.


import optparse

from honeypot.pdf import make_pdf


def generate_pdf(url=None, content=""):
    """
    Generates a PDF and returns it as a string.
    :param content: will be added as text to the PDF
    :param url: the PDF will ping this URL when opened
    :return:
    """

    pdf_string_io = make_pdf.PDFStringIO()
    # import mPDF
    # oPDF = mPDF.cPDF(output_file_name)  # for a real file
    pdf_string_io.header()

    open_action = ""
    if url:
        # there are two ways here: send GET request or POST a form
        open_action = "/OpenAction << /S /URI /URI ({url}) >>".format(url=url)
        # open_action = "<</S /SubmitForm /F << /FS /URL /F ({url}) >> >>".format(url=url.rstrip("/") + "-form/")

    pdf_string_io.indirectobject(1, 0, '<<\n /Type /Catalog\n /Outlines 2 0 R\n /Pages 3 0 R\n {open_action}\n>>'.format(
        open_action=open_action))
    pdf_string_io.indirectobject(2, 0, '<<\n /Type /Outlines\n /Count 0\n>>')
    pdf_string_io.indirectobject(3, 0, '<<\n /Type /Pages\n /Kids [4 0 R]\n /Count 1\n>>')
    pdf_string_io.indirectobject(4, 0, '<<\n /Type /Page\n /Parent 3 0 R\n /MediaBox [0 0 612 792]\n /Contents 5 0 R\n /Resources <<\n             /ProcSet [/PDF /Text]\n             /Font << /F1 6 0 R >>\n            >>\n>>')
    pdf_string_io.stream(5, 0, 'BT /F1 12 Tf 100 700 Td 15 TL ({content}) Tj ET'.format(content=content))
    pdf_string_io.indirectobject(6, 0, '<<\n /Type /Font\n /Subtype /Type1\n /Name /F1\n /BaseFont /Helvetica\n /Encoding /MacRomanEncoding\n>>')

    pdf_string_io.xrefAndTrailer('1 0 R')

    return pdf_string_io.finish()


def Main():
    """
    make-pdf-phone-home, use it to create a PDF document that automatically sends requests to a url when the document
    is opened
    """

    parser = optparse.OptionParser(usage='usage: %prog url', version='%prog 0.1')
    (_, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        print("")
        print(
            '  make-pdf-phone-home, use it to create a PDF document that automatically sends requests to a url when the document is opened')
        print('  Based on make-pdf by https://DidierStevens.com')

    else:
        url = args[1]
        print(generate_pdf(url))


if __name__ == '__main__':
    Main()
