import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { AskResponse } from '../../types/ask.types';
import { postAsk } from '../../api/askApi';
import { toast } from 'react-hot-toast';

interface AskState {
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  result: AskResponse | null;
  error: string | null;
  lastQuestion: string | null;
}

const initialState: AskState = {
  status: 'idle',
  result: null,
  error: null,
  lastQuestion: null,
};

export const submitQuestion = createAsyncThunk<
  AskResponse,
  string,
  { rejectValue: string }
>(
  'ask/submitQuestion',
  async (question, { rejectWithValue }) => {
    try {
      const response = await postAsk({ question });
      
      // Success toast on finding an answer
      if (response.grounded) {
        toast.success('Answer found');
      }

      return response;
    } catch (err: any) {
      // The interceptor handles the network error toast, 
      // but we can also reject with a string here for state.
      const message = err.response?.data?.detail || err.message || 'Failed to submit question';
      return rejectWithValue(message);
    }
  }
);

const askSlice = createSlice({
  name: 'ask',
  initialState,
  reducers: {
    resetAskState(state) {
      state.status = 'idle';
      state.result = null;
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitQuestion.pending, (state, action) => {
        state.status = 'loading';
        state.error = null;
        state.lastQuestion = action.meta.arg;
        state.result = null; // Clear previous result while loading
      })
      .addCase(submitQuestion.fulfilled, (state, action: PayloadAction<AskResponse>) => {
        state.status = 'succeeded';
        state.result = action.payload;
      })
      .addCase(submitQuestion.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload ?? 'Unknown error';
      });
  },
});

export const { resetAskState } = askSlice.actions;
export default askSlice.reducer;
