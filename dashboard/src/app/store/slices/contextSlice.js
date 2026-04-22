import { createSlice } from '@reduxjs/toolkit';
/**
 * Context slice to manage application context such as language, theme, and session token.
 */
const contextSlice = createSlice({
    name: 'context',
    initialState:{
        lang:'es',
        theme:'light'
    },
    reducers:{
        setLanguaje:(state, action) => {
            state.lang = action.payload;
        },
        setTheme:(state, action) => {
            state.theme = action.payload;
        },
        setSession:(state, action) => {
            state.session = action.payload;
        }
    }
});

export const { setLanguaje,  setTheme, setSession } =  contextSlice.actions;
export default contextSlice.reducer;