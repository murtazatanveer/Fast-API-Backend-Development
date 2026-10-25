import React from "react";

const PatientCard = ({ patient, onEdit, onDelete }) => {
  // Helper function to handle verdict colors safely
  const getVerdictStyle = (verdict) => {
    switch (verdict) {
      case "Underweight":
        return "bg-sky-100 text-sky-700 border-sky-200"; // Blueish
      case "Normal":
        return "bg-emerald-100 text-emerald-700 border-emerald-200"; // Green
      case "Overweight":
        return "bg-amber-100 text-amber-700 border-amber-200"; // Orange/Yellow
      case "Obese":
        return "bg-rose-100 text-rose-700 border-rose-200"; // Red
      default:
        return "bg-gray-100 text-gray-700 border-gray-200";
    }
  };

  return (
    <tr className="hover:bg-blue-50/40 transition-colors duration-200 group even:bg-gray-50/30">
      {/* ID */}
      <td className="px-6 py-4 whitespace-nowrap border-r border-gray-100/50">
        <span className="font-mono text-sm font-medium text-blue-600 bg-blue-50 px-2.5 py-1 rounded-md border border-blue-100">
          {patient.id}
        </span>
      </td>

      {/* Name */}
      <td className="px-6 py-4 whitespace-nowrap font-semibold text-gray-900 border-r border-gray-100/50">
        {patient.name}
      </td>

      {/* Age */}
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 border-r border-gray-100/50">
        {patient.age}
      </td>

      {/* City */}
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 border-r border-gray-100/50">
        {patient.city}
      </td>

      {/* Gender */}
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize border-r border-gray-100/50">
        {patient.gender}
      </td>

      {/* Height */}
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 border-r border-gray-100/50">
        {patient.height} m
      </td>

      {/* Weight */}
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 border-r border-gray-100/50">
        {patient.weight} kg
      </td>

      {/* BMI */}
      <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900 border-r border-gray-100/50">
        {patient.bmi}
      </td>

      {/* Verdict (Separated Column with dynamic colors) */}
      <td className="px-6 py-4 whitespace-nowrap border-r border-gray-100/50">
        <span
          className={`text-[11px] font-bold px-2.5 py-1 rounded-md uppercase tracking-wide border ${getVerdictStyle(patient.verdict)}`}
        >
          {patient.verdict}
        </span>
      </td>

      {/* Actions */}
      <td className="px-6 py-4 whitespace-nowrap text-right">
        <div className="flex items-center justify-end gap-2 md:opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <button
            onClick={() => onEdit && onEdit(patient)}
            className="p-2 text-blue-600 bg-white border border-gray-200 hover:bg-blue-50 hover:border-blue-200 rounded-lg transition-all shadow-sm"
            title="Edit Patient"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
          </button>

          <button
            onClick={() => onDelete && onDelete(patient)}
            className="p-2 text-red-600 bg-white border border-gray-200 hover:bg-red-50 hover:border-red-200 rounded-lg transition-all shadow-sm"
            title="Delete Patient"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </td>
    </tr>
  );
};

export default PatientCard;
