import { useDispatch, useSelector } from 'react-redux';
import type { AppDispatch, RootState } from '../store/store';
import { submitQuestion, resetAskState } from '../store/slices/askSlice';
import { useCallback } from 'react';

export const useAsk = () => {
  const dispatch = useDispatch<AppDispatch>();
  const state = useSelector((state: RootState) => state.ask);

  const askQuestion = useCallback(
    (question: string) => {
      dispatch(submitQuestion(question));
    },
    [dispatch]
  );

  const reset = useCallback(() => {
    dispatch(resetAskState());
  }, [dispatch]);

  return {
    ...state,
    askQuestion,
    reset,
  };
};
