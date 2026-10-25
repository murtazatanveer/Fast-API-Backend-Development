// Authentication/components/AuthHeader.jsx
export const AuthHeader = ({ icon, title, subtitle }) => (
  <div className="text-center mb-8">
    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 text-white shadow-lg shadow-blue-500/30 mb-4 transform transition-transform hover:scale-105">
      {icon}
    </div>
    <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">
      {title}
    </h2>
    <p className="text-sm text-gray-500 mt-2">{subtitle}</p>
  </div>
);
