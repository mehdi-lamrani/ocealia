import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode

def color_stock_values():
    return JsCode("""
    function(params) {
        if (params.value < 0) {
            return {
                'color': 'black',
                'backgroundColor': 'aquamarine'
            }
        } else if (params.value == 0) {
            return {
                'color': 'black',
                'backgroundColor': 'pink'
            }
        }
    }
    """)

# Hardcoded filename (replace with your actual file path)
filename = "/workspace/ocealia/data/stage_synthese_produit.csv"

df = pd.read_csv(filename, sep=';')  
df['RESTE_A_STOCKER'] = pd.to_numeric(df['RESTE_A_STOCKER'], errors='coerce')


st.set_page_config(layout="wide")

tab1, tab2 = st.tabs(["Produit Synthese", "Stockage/Transfert"])

# Content for the first tab
with tab1:
    st.title("Produit Synthese")

    # Configure the grid options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection('single', use_checkbox=False)
    gb.configure_column('RESTE_A_STOCKER', cellStyle=color_stock_values())
    grid_options = gb.build()

    # Display the DataFrame with AgGrid
    AgGrid(df, gridOptions=grid_options, height=500, width='100%', fit_columns_on_grid_load=True, allow_unsafe_jscode=True)


with tab2:
    produit_df = pd.read_csv('/workspace/ocealia/data/produit.csv', sep=';')
    produit_list = produit_df['PRODUIT'].unique()
    
    # Filter based on selected product
    stockage_df = pd.read_csv('/workspace/ocealia/data/stage_stockage_df.csv', sep=';')

    produit_code_stockage_list = stockage_df['CODE_PRODUIT_STOCKAGE'].unique()
    produit_list_in_table = produit_df[produit_df['CODE_PRODUIT_STOCKAGE'].isin(produit_code_stockage_list)]['PRODUIT'].unique()

   # Modify the display names for the dropdown with counts
    modified_produit_list = []
    for produit in produit_list:
        produit_code_stockage = produit_df[produit_df['PRODUIT'] == produit]['CODE_PRODUIT_STOCKAGE'].values[0]
        count = stockage_df[stockage_df['CODE_PRODUIT_STOCKAGE'] == produit_code_stockage].shape[0]
        modified_produit_list.append(f"({count}) {produit}")

    # Create a dropdown with modified display names
    selected_produit = st.selectbox("Select a Produit:", modified_produit_list)

    #
    if selected_produit.startswith("(0)"):
        produit_code_stockage = 0
    else :
        produit_code_stockage = produit_df[produit_df['PRODUIT'] == selected_produit[4:]]['CODE_PRODUIT_STOCKAGE'].values[0]

    st.write(f"Selected Produit: {selected_produit[4:]}")
    st.write(f"Code Produit: {produit_code_stockage}")

    subtab1, subtab2 = st.tabs(["Stockage", "Transfert"])

    with subtab1:
        st.title("Stockage")    
        stockage_df = pd.read_csv('/workspace/ocealia/data/stage_stockage_df.csv', sep=';')
        filtered_df = stockage_df[stockage_df['CODE_PRODUIT_STOCKAGE'] == produit_code_stockage]    
        filtered_df = filtered_df[["CODE_SITE","NOM_SITE","SECTEUR","QTE_PREV_EQ_BLE","TRANSFERT_ENTRANT","TRANSFERT_SORTANT","CAPACITE","ECART"]]
        #st.dataframe(filtered_df, use_container_width=True)

        gb = GridOptionsBuilder.from_dataframe(filtered_df)
        gb.configure_selection('single', use_checkbox=False)
        grid_options = gb.build()

        # Display the DataFrame with AgGrid
        AgGrid(filtered_df, gridOptions=grid_options, height=500, width='100%', fit_columns_on_grid_load=True, allow_unsafe_jscode=True)



    with subtab2:
        st.title("Transfert")      
        stockage_df = pd.read_csv('/workspace/ocealia/data/stage_stockage_df.csv', sep=';')
        filtered_df = stockage_df[stockage_df['CODE_PRODUIT_STOCKAGE'] == produit_code_stockage]
        filtered_df = filtered_df[["CODE_SITE","NOM_SITE","SECTEUR","QTE_PREV_EQ_BLE","TRANSFERT_ENTRANT","CAPACITE","QUANTITE_A_TRANSFERER","DEST_T1","DEST_T1_NOM_SITE","COUT_T1","QTE_T1"]]
        filtered_df.reset_index(inplace=True)
        filtered_df.rename(columns={'index': 'ORIGINAL_INDEX'}, inplace=True)
    

        gb = GridOptionsBuilder.from_dataframe(filtered_df)
        gb.configure_selection('single', use_checkbox=False)
        grid_options = gb.build()
        
        # Display the DataFrame with AgGrid
        grid_response = AgGrid(filtered_df, gridOptions=grid_options, height=500, width='100%', fit_columns_on_grid_load=True, allow_unsafe_jscode=True, update_mode=GridUpdateMode.MODEL_CHANGED, enable_enterprise_modules=True)

        # Add a dropdown list for NOM_SITE
        site_df = pd.read_csv('/workspace/ocealia/data/site.csv', sep=';')
        nom_site_list = site_df["NOM_SITE"].unique()
        selected_nom_site = st.selectbox("Select NOM_SITE:", nom_site_list)

        selected_rows = grid_response['selected_rows']

        if selected_rows is not None :
            original_index = selected_rows.iloc[0]['ORIGINAL_INDEX']
            if selected_nom_site:
                filtered_df.loc[filtered_df['ORIGINAL_INDEX'] == original_index, 'DEST_T1_NOM_SITE'] = selected_nom_site
                # Apply the change to the AG Grid
                grid_api = grid_response['api']
                row_node = grid_api.getRowNode(original_index)
                if row_node:
                    row_node.setDataValue('DEST_T1_NOM_SITE', selected_nom_site)

    # Redisplay the updated DataFrame with AgGrid
    AgGrid(filtered_df, gridOptions=grid_options, height=500, width='100%', fit_columns_on_grid_load=True, allow_unsafe_jscode=True)
