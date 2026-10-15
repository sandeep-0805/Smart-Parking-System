import React, { useState, useEffect } from 'react';
import { FiClock } from 'react-icons/fi';

export const Countdown = ({ initialSeconds = 600, onExpire, label = 'Hold expires in' }) => {
  const [secondsLeft, setSecondsLeft] = useState(initialSeconds);

  useEffect(() => {
    setSecondsLeft(initialSeconds);
  }, [initialSeconds]);

  useEffect(() => {
    if (secondsLeft <= 0) {
      if (onExpire) onExpire();
      return;
    }

    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          if (onExpire) onExpire();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [secondsLeft, onExpire]);

  const mins = Math.floor(secondsLeft / 60);
  const secs = secondsLeft % 60;
  const isUrgent = secondsLeft < 120; // under 2 minutes

  if (secondsLeft <= 0) {
    return (
      <div className="inline-flex items-center text-xs font-semibold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-md border border-rose-200">
        <FiClock className="mr-1.5" /> Hold expired
      </div>
    );
  }

  return (
    <div
      className={`inline-flex items-center text-xs font-semibold px-2.5 py-1 rounded-md border transition-colors ${
        isUrgent
          ? 'text-rose-600 bg-rose-50 border-rose-200 animate-pulse'
          : 'text-amber-700 bg-amber-50 border-amber-200'
      }`}
    >
      <FiClock className="mr-1.5" />
      {label}: {mins}:{secs < 10 ? `0${secs}` : secs}
    </div>
  );
};
