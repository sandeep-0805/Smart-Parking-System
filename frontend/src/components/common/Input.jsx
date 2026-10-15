import React from 'react';
import clsx from 'clsx';

export const Input = ({
  label,
  error,
  helperText,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || props.name;

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={clsx(
          'w-full px-3.5 py-2 text-sm bg-white border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors',
          error
            ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-200 text-rose-900'
            : 'border-slate-300 focus:border-blue-500 focus:ring-blue-100 text-slate-900',
          className
        )}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-rose-600 font-medium">{error}</p>}
      {!error && helperText && <p className="mt-1 text-xs text-slate-500">{helperText}</p>}
    </div>
  );
};
