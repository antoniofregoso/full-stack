import { createSlice } from '@reduxjs/toolkit';

const byeSlice = createSlice({
    name: 'bye',
    initialState:{
        stage:'awaiting',
        scrollStopping:{
            page:{
                req:{},
                name:'',
                session:'',
                start:0,
                end:0,
                time:0,
                leavingApp:0,
                views:0
            },
        }
        
    },
    reducers:{
        setStage:(state, action) => {
            state.stage = action.payload;
        },
        setScrollStopping:(state, action) => {
            state.scrollStopping = action.payload;
        } 
    }
});

export const { setStage, setScrollStopping } =  byeSlice.actions;
export default byeSlice.reducer;