from flask import Blueprint, abort, render_template, request

from app.services.disease_service import DiseaseService

# =====================================================
# PUBLIC BLUEPRINT
# =====================================================

public_bp = Blueprint(
    'public',
    __name__,
    url_prefix=''
)


# =====================================================
# 1. HOME PAGE
# URL: /
# =====================================================

@public_bp.route('/')
def home():
    return render_template(
        'public/home.html'
    )


# =====================================================
# 2. ABOUT CAMBODIAN RICE
# URL: /about-rice
# =====================================================

@public_bp.route('/about-rice')
def about_rice():
    return render_template(
        'public/about_rice.html'
    )


# =====================================================
# 3. RICE VARIETIES
# URL: /rice-varieties
# =====================================================

@public_bp.route('/rice-varieties')
def rice_varieties():
    return render_template(
        'public/rice_varieties.html'
    )


# =====================================================
# 4. RICE CULTIVATION
# URL: /cultivation
# =====================================================

@public_bp.route('/cultivation')
def cultivation():
    return render_template(
        'public/cultivation.html'
    )


# =====================================================
# 5. RICE DISEASES
# URL: /diseases
# =====================================================

@public_bp.route('/diseases')
def diseases():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    disease_type = request.args.get('type', '')
    severity = request.args.get('severity', '')

    return render_template(
        'public/diseases.html',
        diseases=DiseaseService.search_public_diseases(q, disease_type, severity, page, per_page=9),
        types=DiseaseService.get_disease_types(),
        severities=DiseaseService.get_severity_levels(),
        q=q, disease_type=disease_type, severity=severity,
    )


# =====================================================
# 6. DISEASE DETAILS
# URL: /diseases/<disease_id>
# =====================================================

@public_bp.route('/diseases/<int:disease_id>')
def disease_detail(disease_id):
    disease = DiseaseService.get_active_disease_by_id(disease_id)
    if disease is None:
        abort(404)

    return render_template(
        'public/disease_detail.html',
        disease=disease,
        other_diseases=DiseaseService.get_other_diseases(disease_id, limit=3),
    )


# =====================================================
# 7. DISEASE PREVENTION
# URL: /prevention
# =====================================================

@public_bp.route('/prevention')
def prevention():
    return render_template(
        'public/prevention.html'
    )
@public_bp.route('/treatment')
def treatment():
    return render_template('public/treatment.html')