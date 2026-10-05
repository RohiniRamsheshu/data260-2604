import axios from "axios";
import {
  configureStore,
  createAsyncThunk,
  createSlice,
} from "@reduxjs/toolkit";

const api = axios.create({
  baseURL: "http://localhost:8804",
  withCredentials: true,
});

export const fetchVulnerabilities = createAsyncThunk(
  "vulnerabilities/fetch",
  async (_, thunkAPI) => {
    try {
      const response = await api.get("/api/vulnerabilities");
      return response.data;
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error.response?.data?.detail || "Unable to fetch vulnerabilities"
      );
    }
  }
);

export const createVulnerability = createAsyncThunk(
  "vulnerabilities/create",
  async (vulnerability, thunkAPI) => {
    try {
      const response = await api.post(
        "/api/vulnerabilities",
        vulnerability
      );
      return response.data;
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error.response?.data?.detail || "Unable to create vulnerability"
      );
    }
  }
);

export const updateVulnerability = createAsyncThunk(
  "vulnerabilities/update",
  async ({ id, data }, thunkAPI) => {
    try {
      const response = await api.put(
        `/api/vulnerabilities/${id}`,
        data
      );
      return response.data;
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error.response?.data?.detail || "Unable to update vulnerability"
      );
    }
  }
);

export const deleteVulnerability = createAsyncThunk(
  "vulnerabilities/delete",
  async (id, thunkAPI) => {
    try {
      await api.delete(`/api/vulnerabilities/${id}`);
      return id;
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error.response?.data?.detail || "Unable to delete vulnerability"
      );
    }
  }
);

const vulnerabilitySlice = createSlice({
  name: "vulnerabilities",

  initialState: {
    records: [],
    status: "idle",
    error: null,
  },

  reducers: {},

  extraReducers: (builder) => {
    builder
      .addCase(fetchVulnerabilities.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchVulnerabilities.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.records = action.payload;
      })
      .addCase(fetchVulnerabilities.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      })

      .addCase(createVulnerability.fulfilled, (state, action) => {
        state.records.push(action.payload);
      })

      .addCase(updateVulnerability.fulfilled, (state, action) => {
        const index = state.records.findIndex(
          (record) => record.id === action.payload.id
        );

        if (index !== -1) {
          state.records[index] = action.payload;
        }
      })

      .addCase(deleteVulnerability.fulfilled, (state, action) => {
        state.records = state.records.filter(
          (record) => record.id !== action.payload
        );
      });
  },
});

export const store = configureStore({
  reducer: {
    vulnerabilities: vulnerabilitySlice.reducer,
  },
});
