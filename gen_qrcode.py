from qrcode import QRCode
import qrcode.constants

form_url = 'https://derryrockautomation.onrender.com'

qr = QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(form_url)
qr.make(fit=True)

img = qr.make_image(fill='black', back_color='white')
img.save('QRcode.png')
print("QR code generated and saved as 'QRcode.png'.")
