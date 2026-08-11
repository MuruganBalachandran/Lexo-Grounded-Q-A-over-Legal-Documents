import { configureStore } from '@reduxjs/toolkit';
import askReducer from './slices/askSlice';

export const store = configureStore({
  reducer: {
    ask: askReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
