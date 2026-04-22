import { configureStore, combineReducers } from "@reduxjs/toolkit";
import { persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import contextSlice from "./slices/contextSlice";
import homeSlice from "./slices/homeSlice";
import byeSlice from "./slices/byeSlice";
/**
 * Configure the Redux store with slices and persistence.
 */
const persistConfig = {
  key: 'root',
  storage
};
/**
 * Combine the slices into a root reducer.
 */
const rootReducer = combineReducers({
  context: contextSlice,
  home: homeSlice,
  bye: byeSlice
});
/**
 * Create a persisted reducer using the root reducer and persistence configuration.
 */
const persistedReducer = persistReducer(persistConfig, rootReducer);
/**
 * Configure the Redux store with the persisted reducer.
 */
const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      }
    })
});
/**
 * Create a persistor to manage the persistence of the store.
 */
const persistor = persistStore(store);

export { store, persistor };
