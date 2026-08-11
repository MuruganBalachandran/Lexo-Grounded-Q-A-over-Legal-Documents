import { axiosClient } from './axiosClient';
import type { AskRequest, AskResponse } from '../types/ask.types';

export const postAsk = async (request: AskRequest): Promise<AskResponse> => {
  const response = await axiosClient.post<AskResponse>('/ask', request);
  return response.data;
};
