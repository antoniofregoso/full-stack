import { createSlice } from '@reduxjs/toolkit';
/**
 * Home slice to manage the state of the home component, including stage and scroll stoping.
 */
const homeSlice = createSlice({
    name: 'home',
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
        },
        setSectionTracking:(state, action) => {
            let section = Object.keys(action.payload)[0];
            state.scrollStopping.sections[section] = action.payload[section];
        },
        setEscapeAttempt:(state, action) => {
            state.scrollStopping.page.leavingapp = action.payload;
        }
    }
});

export const { setStage, setScrollStopping, setSectionTracking, setEscapeAttempt } =  homeSlice.actions;
export default homeSlice.reducer;