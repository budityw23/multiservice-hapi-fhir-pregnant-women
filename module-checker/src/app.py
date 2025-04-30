from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@checklist-db:5432/checklist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('ChecklistItem', backref='module', lazy=True, cascade='all, delete-orphan')

class ChecklistItem(db.Model):
    __tablename__ = 'checklist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    display = db.Column(db.String(200), nullable=False)
    system = db.Column(db.String(200), default='http://loinc.org')
    required = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    modules = Module.query.all()
    return render_template('index.html', modules=modules)

@app.route('/module/<int:module_id>')
def view_module(module_id):
    module = Module.query.get_or_404(module_id)
    return render_template('module.html', module=module)


@app.route('/module/new', methods=['GET', 'POST'])
def new_module():
    if request.method == 'POST':
        module = Module(
            name=request.form['name'],
            description=request.form['description']
        )
        db.session.add(module)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('module_form.html')
    
@app.route('/module/<int:module_id>/delete', methods=['GET', 'POST'])
def delete_module(module_id):
    module = Module.query.get_or_404(module_id)
    db.session.delete(module)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/module/<int:module_id>/edit', methods=['GET', 'POST'])
def edit_module(module_id):
    module = Module.query.get_or_404(module_id)
    if request.method == 'POST':
        module.name = request.form['name']
        module.description = request.form['description']
        db.session.commit()
        return redirect(url_for('view_module', module_id=module.id))
    return render_template('module_form.html', module=module)

# API endpoints
@app.route('/api/modules', methods=['GET'])
def get_modules():
    modules = Module.query.all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'description': m.description,
        'items_count': len(m.items)
    } for m in modules])

@app.route('/api/modules/<int:module_id>/items', methods=['GET', 'POST'])
def module_items(module_id):
    module = Module.query.get_or_404(module_id)
    
    if request.method == 'POST':
        data = request.get_json()
        item = ChecklistItem(
            module_id=module.id,
            code=data['code'],
            display=data['display'],
            system=data.get('system', 'http://loinc.org'),
            required=data.get('required', False)
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({
            'id': item.id,
            'code': item.code,
            'display': item.display
        })
    
    return jsonify([{
        'id': item.id,
        'code': item.code,
        'display': item.display,
        'required': item.required
    } for item in module.items])

@app.route('/api/modules/<int:module_id>/items/<int:item_id>', methods=['DELETE'])
def delete_item(module_id, item_id):
    item = ChecklistItem.query.filter_by(module_id=module_id, id=item_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001) 