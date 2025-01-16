from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

def load_data():
    try:
        hadm_df = pd.read_csv('./data/numHADM_perAGE-YR-bin.csv')
        obs_df = pd.read_csv('./data/numOBS_perAGE-YR-bin.csv')
        
        # Create single root node for initial view
        root = {
            "id": "PIC",
            "name": "PIC Dataset",
            "type": "root",
            "value": int(hadm_df['num_Unique_HADMs'].sum()),
            "details": {
                "total_admissions": int(hadm_df['num_Unique_HADMs'].sum()),
                "total_observations": int(obs_df['num_Assay_Obs'].sum())
            },
            "children": [
                {
                    "id": "hasCE",
                    "name": "Has CE",
                    "type": "ce_status",
                    "value": int(hadm_df[hadm_df['category'].str.contains('hasCE')]['num_Unique_HADMs'].sum()),
                    "collapsed": True
                },
                {
                    "id": "lacksCE",
                    "name": "No CE",
                    "type": "ce_status",
                    "value": int(hadm_df[hadm_df['category'].str.contains('lacksCE')]['num_Unique_HADMs'].sum()),
                    "collapsed": True
                }
            ]
        }
        
        return {"nodes": [root], "hadm_data": hadm_df.to_dict('records'), "obs_data": obs_df.to_dict('records')}
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    try:
        data = load_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/expand/<node_type>/<node_id>')
def expand_node(node_type, node_id):
    try:
        hadm_df = pd.read_csv('./data/numHADM_perAGE-YR-bin.csv')
        obs_df = pd.read_csv('./data/numOBS_perAGE-YR-bin.csv')
        
        if node_type == 'ce_status':
            # Return age bins for selected CE status
            age_data = hadm_df[hadm_df['category'].str.contains(node_id)].copy()
            age_data['age_bin'] = age_data['category'].str.extract(r'yrBIN_(\d+)').astype(int)
            
            children = []
            for age in range(1, 19):
                age_count = age_data[age_data['age_bin'] == age]['num_Unique_HADMs'].iloc[0]
                children.append({
                    "id": f"{node_id}_age{age}",
                    "name": f"Age {age-1}-{age}",
                    "type": "age_bin",
                    "value": int(age_count),
                    "collapsed": True
                })
            
            return jsonify({"children": children})
            
        elif node_type == 'age_bin':
            # Return lab items for selected age bin
            ce_status = node_id.split('_')[0]
            age = node_id.split('_')[1].replace('age', '')
            
            lab_data = obs_df[obs_df['category'].str.contains(f"{ce_status}_AGE_yrBIN_{age}_item")].copy()
            lab_data['lab_item'] = lab_data['category'].str.extract(r'item_(\d+)').astype(int)
            
            children = []
            for _, row in lab_data.iterrows():
                children.append({
                    "id": f"{node_id}_lab{row['lab_item']}",
                    "name": f"Lab {row['lab_item']}",
                    "type": "lab_item",
                    "value": int(row['num_Assay_Obs'])
                })
            
            return jsonify({"children": children})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)