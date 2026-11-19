# First, create your project folder and enter it:
mkdir Rice-Disease-System
cd Rice-Disease-System

# Step 1 — Create all folders
mkdir app\config app\routes app\services app\models app\forms app\repositories app\utils app\extensions app\templates\errors app\templates\auth app\templates\dashboard app\templates\users app\templates\farms app\templates\fields app\templates\diagnosis app\templates\diseases app\templates\monitoring app\templates\treatments app\templates\reports app\static\css app\static\js app\static\images app\static\uploads app\api\routes app\api\services app\api\schemas migrations tests docs scripts

# Step 2 — Create all Python files
type nul > app\__init__.py

type nul > app\config\__init__.py
type nul > app\config\settings.py

type nul > app\routes\__init__.py
type nul > app\routes\auth_routes.py
type nul > app\routes\dashboard_routes.py
type nul > app\routes\user_routes.py
type nul > app\routes\farm_routes.py
type nul > app\routes\field_routes.py
type nul > app\routes\diagnosis_routes.py
type nul > app\routes\disease_routes.py
type nul > app\routes\monitoring_routes.py
type nul > app\routes\treatment_routes.py
type nul > app\routes\notification_routes.py
type nul > app\routes\report_routes.py

type nul > app\services\__init__.py
type nul > app\services\auth_service.py
type nul > app\services\user_service.py
type nul > app\services\farm_service.py
type nul > app\services\field_service.py
type nul > app\services\diagnosis_service.py
type nul > app\services\disease_service.py
type nul > app\services\monitoring_service.py
type nul > app\services\treatment_service.py
type nul > app\services\report_service.py

type nul > app\models\__init__.py
type nul > app\models\user_model.py
type nul > app\models\role_model.py
type nul > app\models\permission_model.py
type nul > app\models\farm_model.py
type nul > app\models\field_model.py
type nul > app\models\field_crop_model.py
type nul > app\models\disease_model.py
type nul > app\models\diagnosis_model.py
type nul > app\models\monitoring_model.py
type nul > app\models\treatment_model.py
type nul > app\models\notification_model.py

type nul > app\forms\__init__.py
type nul > app\forms\login_form.py
type nul > app\forms\register_form.py
type nul > app\forms\user_form.py
type nul > app\forms\farm_form.py
type nul > app\forms\field_form.py
type nul > app\forms\diagnosis_form.py

type nul > app\repositories\__init__.py
type nul > app\repositories\user_repository.py
type nul > app\repositories\farm_repository.py
type nul > app\repositories\field_repository.py
type nul > app\repositories\diagnosis_repository.py
type nul > app\repositories\disease_repository.py

type nul > app\utils\__init__.py
type nul > app\utils\decorators.py
type nul > app\utils\validators.py
type nul > app\utils\helpers.py
type nul > app\utils\constants.py
type nul > app\utils\permissions.py

type nul > app\extensions\__init__.py
type nul > app\extensions\database.py
type nul > app\extensions\login_manager.py
type nul > app\extensions\csrf.py

type nul > app\api\__init__.py
type nul > app\api\routes\__init__.py
type nul > app\api\services\__init__.py
type nul > app\api\schemas\__init__.py

type nul > tests\__init__.py
type nul > tests\test_auth.py
type nul > tests\test_users.py
type nul > tests\test_farms.py
type nul > tests\test_diagnosis.py

type nul > docs\api_documentation.md
type nul > docs\database_documentation.md

type nul > scripts\seed_data.py
type nul > scripts\create_admin.py

type nul > app\templates\base.html
type nul > app\templates\errors\403.html
type nul > app\templates\errors\404.html
type nul > app\templates\errors\500.html

type nul > app\static\css\style.css
type nul > app\static\css\responsive.css

type nul > app\static\js\main.js
type nul > app\static\js\diagnosis.js

type nul > .env
type nul > .env.example
type nul > .gitignore
type nul > requirements.txt
type nul > config.py
type nul > run.py
type nul > README.md


# Step 3 — Verify your folder structure
tree /F

3. What each folder is responsible for
Folder	        Responsibility
routes/	        Handles URLs, HTTP requests and responses
services/	    Business logic, calculations and system operations
models/	        Database models and relationships
forms/	        Form validation and input handling
repositories/	Database queries and CRUD operations
utils/	        Helper functions, decorators and utilities
extensions/	    Flask extensions such as SQLAlchemy
config/	        Application settings and configurations
templates/	    HTML pages rendered using Jinja2
static/	        CSS, JavaScript, images and uploaded assets
api/	        API endpoints and API-specific logic
migrations/	    Database schema change history
tests/	        Automated tests
docs/	        Documentation
scripts/	    Setup scripts, seeding and admin creation