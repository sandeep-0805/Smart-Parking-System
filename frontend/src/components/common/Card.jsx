import React from 'react';
import clsx from 'clsx';

export const Card = ({ children, className = '', hover = false, ...props }) => {
  return (
    <div
      className={clsx(
        'bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden',
        hover && 'hover:shadow-md hover:border-slate-300 transition-all duration-200',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
