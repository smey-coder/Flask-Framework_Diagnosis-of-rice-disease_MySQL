from flask_wtf import form


print("FORM IMAGE:", form.image.data)
print("FILENAME:", form.image.data.filename if form.image.data else "None")