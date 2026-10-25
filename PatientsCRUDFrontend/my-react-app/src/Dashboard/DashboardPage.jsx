import { useEffect, useState } from "react";
import { fetchApi } from "../Utils/apiClient";
import AddPatientModal from "./components/AddPatientModal";
import PatientCard from "./components/PatientCard";
import LogoutMenu from "./components/LogoutMenu"; // <-- Import LogoutMenu

const DashboardPage = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchPatients = async () => {
    try {
      const response = await fetchApi("/patients", { method: "GET" });
      if (response.ok) {
        const data = await response.json();
        setPatients(data.data);
      } else {
        setPatients([]);
      }
    } catch (err) {
      setPatients([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleEdit = (patient) => {
    console.log("Edit patient:", patient);
  };

  const handleDelete = (patient) => {
    console.log("Delete patient:", patient);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
          <p className="text-gray-500 font-medium">Loading your patients...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] p-6 md:p-10 font-sans relative">
      <AddPatientModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onPatientAdded={fetchPatients}
      />

      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
              Patient Dashboard
            </h1>
            <p className="text-gray-500 mt-1">
              Manage your patients and their health records.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-5 py-2.5 rounded-xl font-semibold shadow-lg shadow-blue-500/30 transform hover:-translate-y-0.5 transition-all duration-200"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Add Patient
            </button>

            {/* Replace the old Logout button with the LogoutMenu */}
            <LogoutMenu onLogoutSuccess={() => {}} />
          </div>
        </div>

        {/* Empty State */}
        {patients.length === 0 && (
          <div className="bg-white rounded-3xl p-12 text-center border border-gray-100 shadow-sm">
            <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-10 h-10 text-blue-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900">
              No patients found
            </h3>
            <p className="text-gray-500 mt-2 max-w-sm mx-auto">
              You haven't added any patients yet. Click the "Add Patient" button
              to get started.
            </p>
          </div>
        )}

        {/* Premium Patients Table */}
        {patients.length > 0 && (
          <div className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-200/60 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50/80 border-b border-gray-200/60">
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider border-r border-gray-200/60">
                      ID
                    </th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider border-r border-gray-200/60">
                      Name
                    </th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider border-r border-gray-200/60">
                      Age
                    </th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider border-r border-gray-200/60">
                      City
                    </th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider border-r border-gray-200/60">
                      Gender
                    </th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider border-r border-gray-200/60">
                      Height
                    </th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider border-r border-gray-200/60">
                      Weight
                    </th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider border-r border-gray-200/60">
                      BMI
                    </th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider border-r border-gray-200/60">
                      Verdict
                    </th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {patients.map((patient) => (
                    <PatientCard
                      key={patient.id}
                      patient={patient}
                      onEdit={handleEdit}
                      onDelete={handleDelete}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
