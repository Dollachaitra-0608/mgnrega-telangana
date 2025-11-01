import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function App() {
  const [districts, setDistricts] = useState([]);
  const [performance, setPerformance] = useState([]);
  const [selectedDistrict, setSelectedDistrict] = useState("");

  // ✅ Use your deployed backend URL on Railway
  const BASE_URL = "https://mgnrega-telangana-production.up.railway.app";

  // 1️⃣ Fetch district names from backend
  useEffect(() => {
    axios
      .get(`${BASE_URL}/districts`)
      .then((res) => {
        setDistricts(res.data);
      })
      .catch((err) => console.error("Error fetching districts:", err));
  }, []);

  // 2️⃣ Bonus: Log user location (future improvement)
  useEffect(() => {
    navigator.geolocation.getCurrentPosition((pos) => {
      console.log(
        "Latitude:",
        pos.coords.latitude,
        "Longitude:",
        pos.coords.longitude
      );
    });
  }, []);

  // 3️⃣ Fetch performance data for selected district
  const fetchPerformance = (district) => {
    setSelectedDistrict(district);
    axios
      .get(`${BASE_URL}/performance/${district}`)
      .then((res) => {
        setPerformance(res.data);
      })
      .catch((err) => console.error("Error fetching performance:", err));
  };

  return (
    <div
      style={{
        textAlign: "center",
        padding: "20px",
        fontFamily: "Poppins, sans-serif",
        background: "#f8fafc",
        minHeight: "100vh",
      }}
    >
      <h1>🌾 Telangana MGNREGA Dashboard</h1>
      <p>Select your district to explore monthly performance under MGNREGA</p>

      <select
        onChange={(e) => fetchPerformance(e.target.value)}
        style={{
          padding: "10px",
          fontSize: "16px",
          margin: "10px",
          borderRadius: "8px",
          border: "1px solid #ccc",
        }}
      >
        <option value="">-- Select District --</option>
        {districts.map((d) => (
          <option key={d} value={d}>
            {d}
          </option>
        ))}
      </select>

      {selectedDistrict && (
        <div style={{ marginTop: "40px" }}>
          <h2>📊 District: {selectedDistrict}</h2>
          <ResponsiveContainer width="95%" height={400}>
            <BarChart data={performance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="households" fill="#4caf50" name="Households" />
              <Bar dataKey="persondays" fill="#81c784" name="Persondays" />
              <Bar dataKey="wages" fill="#aed581" name="Wages" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default App;
