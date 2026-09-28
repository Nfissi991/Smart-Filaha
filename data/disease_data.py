# data/disease_data.py

PLANT_NAMES = {
    "Tomato":               {"دارجة": "الطماطم",     "العربية": "الطماطم",      "Français": "Tomate",           "English": "Tomato"},
    "Potato":               {"دارجة": "البطاطس",     "العربية": "البطاطس",      "Français": "Pomme de terre",   "English": "Potato"},
    "Grape":                {"دارجة": "العنب",        "العربية": "العنب",         "Français": "Vigne",            "English": "Grape"},
    "Corn_(maize)":         {"دارجة": "الدرة",        "العربية": "الذرة",         "Français": "Maïs",             "English": "Corn"},
    "Apple":                {"دارجة": "التفاح",       "العربية": "التفاح",        "Français": "Pomme",            "English": "Apple"},
    "Pepper,_bell":         {"دارجة": "الفلفل",       "العربية": "الفلفل",        "Français": "Poivron",          "English": "Pepper"},
    "Strawberry":           {"دارجة": "الفراولة",     "العربية": "الفراولة",      "Français": "Fraise",           "English": "Strawberry"},
    "Cherry_(including_sour)": {"دارجة": "الكرز",    "العربية": "الكرز",         "Français": "Cerise",           "English": "Cherry"},
    "Peach":                {"دارجة": "الخوخ",        "العربية": "الخوخ",         "Français": "Pêche",            "English": "Peach"},
    "Raspberry":            {"دارجة": "التوت",        "العربية": "التوت",         "Français": "Framboise",        "English": "Raspberry"},
    "Blueberry":            {"دارجة": "التوت الأزرق", "العربية": "العنب البري",   "Français": "Myrtille",         "English": "Blueberry"},
    "Soybean":              {"دارجة": "الصويا",       "العربية": "فول الصويا",    "Français": "Soja",             "English": "Soybean"},
    "Squash":               {"دارجة": "القرع",        "العربية": "القرع",         "Français": "Courge",           "English": "Squash"},
    "Orange":               {"دارجة": "البرتقال",     "العربية": "البرتقال",      "Français": "Orange",           "English": "Orange"},
}

GENERIC_ADVICE = {
    "دارجة":   ["شيل الأجزاء المريضة فوراً", "رش مبيد فطري مناسب واتبع التعليمات", "ما تسقيش بزاف", "استشر خبير زراعي"],
    "العربية": ["أزل الأجزاء المصابة فوراً", "رش مبيداً فطرياً مناسباً", "تجنب الإفراط في الري", "استشر خبيراً زراعياً"],
    "Français": ["Retirez les parties infectées", "Pulvérisez un fongicide adapté", "Évitez l'excès d'arrosage", "Consultez un agronome"],
    "English":  ["Remove infected parts immediately", "Spray appropriate fungicide", "Avoid overwatering", "Consult an agronomist"],
}

DISEASE_DATA = {
    "Tomato___Early_blight": {
        "ar_name":  "اللفحة المبكرة للطماطم",
        "dar_name": "مرض البقعة السوداء ديال الطماطم",
        "fr_name":  "Alternariose de la tomate",
        "en_name":  "Tomato Early Blight",
        "severity": "medium",
        "advice": {
            "دارجة":   ["رش مبيد فطري فيه مانكوزيب أو كلوروثالونيل — كل 7 أيام", "شيل الأوراق المريضة فوراً وحرقهم بعيد على الحقل", "سقي من الجذور في الصباح الباكر — ما تسقيش من فوق", "دوّر المحاصيل — ما تزرعش طماطم في نفس المكان مرتين", "زيد سماد البوتاسيوم باش تقوي مناعة النبتة"],
            "العربية": ["استخدم مبيداً فطرياً يحتوي على المانكوزيب أو الكلوروثالونيل — رش كل 7 أيام", "أزل الأوراق المصابة فوراً واحرقها بعيداً عن الحقل", "اسقِ من الجذور في الصباح الباكر — تجنب الري فوق الأوراق", "دوِّر المحاصيل — لا تزرع طماطم في نفس المكان موسمين متتاليين", "أضف سماداً غنياً بالبوتاسيوم لتعزيز مناعة النبات"],
            "Français": ["Utilisez un fongicide à base de mancozèbe ou chlorothalonil — toutes les 7 jours", "Retirez immédiatement les feuilles infectées et brûlez-les loin du champ", "Arrosez à la base tôt le matin — évitez l'arrosage aérien", "Pratiquez la rotation des cultures — ne replantez pas de tomates au même endroit", "Ajoutez un engrais riche en potassium pour renforcer l'immunité"],
            "English":  ["Use a fungicide containing mancozeb or chlorothalonil — spray every 7 days", "Remove infected leaves immediately and burn them away from the field", "Water at the base early morning — avoid overhead watering", "Rotate crops — do not replant tomatoes in the same spot consecutively", "Add potassium-rich fertilizer to strengthen plant immunity"],
        },
    },
    "Tomato___Late_blight": {
        "ar_name":  "اللفحة المتأخرة للطماطم",
        "dar_name": "مرض العفونة المتأخرة ديال الطماطم",
        "fr_name":  "Mildiou de la tomate",
        "en_name":  "Tomato Late Blight",
        "severity": "high",
        "advice": {
            "دارجة":   ["خطير — رش مبيد فيه ميتالاكسيل في الحال بلا تأخير", "شيل وحرق جميع الأجزاء المريضة قبل ما يتفشى", "سقي في الصباح فقط باش تجف الأوراق قبل الليل", "رش الكبريت كمركب وقائي قبل موسم المطر", "خبر الفلاحين المجاورين — المرض يتنقل بسرعة"],
            "العربية": ["خطير جداً — رش مبيداً يحتوي على الميتالاكسيل فوراً بدون تأخير", "أزل وأحرق جميع الأجزاء المصابة قبل انتشار المرض", "اسقِ صباحاً فقط حتى تجف الأوراق قبل المساء", "رش الكبريت كمادة وقائية قبل موسم الأمطار", "أبلغ الفلاحين المجاورين — المرض يتنقل بسرعة كبيرة"],
            "Français": ["Très grave — pulvérisez immédiatement un fongicide contenant du métalaxyl", "Retirez et brûlez toutes les parties infectées sans délai", "Arrosez uniquement le matin pour que les feuilles sèchent avant le soir", "Pulvérisez du soufre comme mesure préventive avant la saison des pluies", "Informez les agriculteurs voisins — la maladie se propage rapidement"],
            "English":  ["Very serious — spray a fungicide containing metalaxyl immediately", "Remove and burn all infected parts without delay", "Water only in the morning so leaves dry before evening", "Spray sulfur as a preventive measure before the rainy season", "Inform neighboring farmers — the disease spreads quickly"],
        },
    },
    "Tomato___healthy": {
        "ar_name":  "الطماطم سليمة ✓",
        "dar_name": "الطماطم بصحة ✓",
        "fr_name":  "Tomate saine ✓",
        "en_name":  "Tomato Healthy ✓",
        "severity": "none",
        "advice": {
            "دارجة":   ["النبتة بخير! كمل العناية بيها مزيان", "سقي منتظم وسماد كل شهر", "راقب الأوراق أسبوعياً باش تكتشف أي مرض باكر"],
            "العربية": ["النبات سليم! استمر في العناية به", "ري منتظم وتسميد شهري", "راقب الأوراق أسبوعياً للكشف المبكر"],
            "Français": ["Plante saine! Continuez ainsi", "Arrosage régulier et fertilisation mensuelle", "Surveillez les feuilles chaque semaine"],
            "English":  ["Plant is healthy! Keep it up", "Regular watering and monthly fertilization", "Check leaves weekly for early detection"],
        },
    },
    "Potato___Early_blight": {
        "ar_name":  "اللفحة المبكرة للبطاطس",
        "dar_name": "مرض البقعة ديال البطاطس",
        "fr_name":  "Alternariose de la pomme de terre",
        "en_name":  "Potato Early Blight",
        "severity": "medium",
        "advice": {
            "دارجة":   ["رش مبيد فطري فيه كلوروثالونيل أو أزوكسيستروبين", "شيل الأوراق السفلية المريضة باكر قبل ما ينتشر", "خلي مسافة كافية بين النباتات باش يتهوى", "استعمل بذور مصادق عليها وخالية من الأمراض", "تجنب الإفراط في الأزوت ديال السماد"],
            "العربية": ["رش مبيداً فطرياً يحتوي على الكلوروثالونيل أو الأزوكسيستروبين", "أزل الأوراق السفلية المصابة مبكراً قبل انتشار المرض", "حافظ على مسافة كافية بين النباتات لضمان التهوية", "استخدم بذوراً معتمدة وخالية من الأمراض", "تجنب الإفراط في استخدام الأسمدة النيتروجينية"],
            "Français": ["Pulvérisez un fongicide à base de chlorothalonil ou azoxystrobine", "Retirez précocement les feuilles inférieures infectées", "Maintenez un espacement suffisant entre les plants", "Utilisez des semences certifiées et exemptes de maladies", "Évitez l'excès d'engrais azoté"],
            "English":  ["Spray a fungicide containing chlorothalonil or azoxystrobin", "Remove lower infected leaves early before spreading", "Maintain sufficient spacing between plants for ventilation", "Use certified, disease-free seeds", "Avoid excessive nitrogen fertilizer"],
        },
    },
    "Potato___Late_blight": {
        "ar_name":  "اللفحة المتأخرة للبطاطس",
        "dar_name": "عفونة البطاطس المتأخرة",
        "fr_name":  "Mildiou de la pomme de terre",
        "en_name":  "Potato Late Blight",
        "severity": "high",
        "advice": {
            "دارجة":   ["خطير جداً — رش ميتالاكسيل فوراً", "شيل جميع الأجزاء المريضة وحرقهم", "تجنب السقي الزائد والرطوبة العالية", "قلّل النيتروجين وزيد الفوسفور والبوتاسيوم"],
            "العربية": ["خطير جداً — رش الميتالاكسيل فوراً دون تأخير", "أزل جميع الأجزاء المصابة واحرقها", "تجنب الري الزائد والرطوبة العالية", "قلل النيتروجين وزد الفوسفور والبوتاسيوم"],
            "Français": ["Très grave — pulvérisez du métalaxyl immédiatement", "Retirez et brûlez toutes les parties infectées", "Évitez l'excès d'arrosage et l'humidité élevée", "Réduisez l'azote et augmentez phosphore et potassium"],
            "English":  ["Very serious — spray metalaxyl immediately", "Remove and burn all infected parts", "Avoid overwatering and high humidity", "Reduce nitrogen and increase phosphorus and potassium"],
        },
    },
    "Grape___Black_rot": {
        "ar_name":  "العفن الأسود للعنب",
        "dar_name": "مرض العفن الأسود ديال العنب",
        "fr_name":  "Pourriture noire de la vigne",
        "en_name":  "Grape Black Rot",
        "severity": "high",
        "advice": {
            "دارجة":   ["رش مبيد فيه مانكوزيب أو كابتان في بداية الموسم", "شيل العناقيد المريضة والأوراق الميتة فوراً", "قلّم مزيان باش يتهوى الكرم", "ما تسقيش من فوق أبداً", "رش وقائي قبل موسم الأمطار"],
            "العربية": ["رش مبيداً يحتوي على المانكوزيب أو الكابتان في بداية الموسم", "أزل العناقيد المصابة والأوراق الميتة فوراً", "قلِّم الكرمة جيداً لضمان التهوية الكافية", "تجنب الري الرأسي تماماً", "رش وقائي قبل موسم الأمطار"],
            "Français": ["Pulvérisez un fongicide à base de mancozèbe ou captane en début de saison", "Retirez immédiatement grappes infectées et feuilles mortes", "Taillez la vigne correctement pour assurer la ventilation", "Évitez absolument l'arrosage aérien", "Traitement préventif avant la saison des pluies"],
            "English":  ["Spray a fungicide containing mancozeb or captan at season start", "Remove infected clusters and dead leaves immediately", "Prune the vine correctly to ensure good ventilation", "Avoid overhead watering completely", "Preventive spray before the rainy season"],
        },
    },
    "Corn_(maize)___Common_rust_": {
        "ar_name":  "صدأ الذرة الشائع",
        "dar_name": "صدأ الدرة",
        "fr_name":  "Rouille commune du maïs",
        "en_name":  "Corn Common Rust",
        "severity": "medium",
        "advice": {
            "دارجة":   ["رش مبيد فطري فيه تريازول في بداية ظهور المرض", "استعمل أصناف مقاومة للصدأ في الموسم الجاي", "تجنب الزراعة الكثيفة باش يتهوى الحقل", "راقب الحقل كل أسبوع خاصة في الجو الرطب"],
            "العربية": ["رش مبيداً فطرياً يحتوي على التريازول عند أول ظهور للمرض", "استخدم أصناف مقاومة للصدأ في الموسم القادم", "تجنب الزراعة الكثيفة لضمان تهوية جيدة", "راقب الحقل أسبوعياً خاصة في الطقس الرطب"],
            "Français": ["Pulvérisez un fongicide à base de triazole dès les premiers symptômes", "Utilisez des variétés résistantes à la rouille la saison prochaine", "Évitez la densité excessive de plantation", "Surveillez le champ chaque semaine par temps humide"],
            "English":  ["Spray a triazole-based fungicide at first signs of disease", "Use rust-resistant varieties next season", "Avoid excessive planting density", "Monitor the field weekly, especially in humid weather"],
        },
    },
}