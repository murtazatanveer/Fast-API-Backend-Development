// Authentication/components/AuthInput.jsx
export const AuthInput = ({
  label,
  icon,
  type,
  name,
  value,
  onChange,
  placeholder,
  minLength,
}) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-1.5">
      {label}
    </label>
    <div className="relative group">
      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
        <span className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors">
          {icon}
        </span>
      </div>
      <input
        type={type}
        name={name}
        required
        minLength={minLength}
        value={value}
        onChange={onChange}
        className="w-full pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 focus:bg-white transition-all duration-200"
        placeholder={placeholder}
      />
    </div>
  </div>
);
