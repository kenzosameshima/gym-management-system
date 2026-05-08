import "./styles/global.css";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "./contexts/AuthContext";
import { AppRoutes } from "./routes/AppRoutes";

function App(): JSX.Element {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster position="top-right" toastOptions={{ duration: 3000 }} />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
