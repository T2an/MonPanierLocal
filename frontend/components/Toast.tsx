'use client'

import { useEffect, useState } from 'react'

export type ToastType = 'success' | 'error' | 'info'

interface ToastProps {
  message: string
  type?: ToastType
  duration?: number
  onClose?: () => void
  action?: {
    label: string
    onClick: () => void
  }
}

export function Toast({ message, type = 'info', duration = 3000, onClose, action }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false)
        setTimeout(() => onClose?.(), 300) // Attendre la transition
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [duration, onClose])

  if (!isVisible) return null

  const bgColors = {
    success: 'bg-nature-500',
    error: 'bg-red-500',
    info: 'bg-blue-500',
  }

  const icons = {
    success: '✓',
    error: '✕',
    info: 'ℹ',
  }

  return (
    <div
      className={`fixed top-20 right-4 z-50 ${bgColors[type]} text-white px-6 py-4 rounded-2xl shadow-nature-lg flex items-center gap-3 min-w-[300px] max-w-md transform transition-all duration-300 ${
        isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      }`}
    >
      <span className="text-2xl font-bold">{icons[type]}</span>
      <div className="flex-1">
        <p className="font-semibold">{message}</p>
        {action && (
          <button
            onClick={action.onClick}
            className="mt-2 text-sm underline hover:no-underline font-medium"
          >
            {action.label}
          </button>
        )}
      </div>
      <button
        onClick={() => {
          setIsVisible(false)
          setTimeout(() => onClose?.(), 300)
        }}
        className="text-white/80 hover:text-white text-xl font-bold"
      >
        ×
      </button>
    </div>
  )
}

interface ToastContainerProps {
  toasts: Array<{ id: string; message: string; type?: ToastType; action?: { label: string; onClick: () => void } }>
  onRemove: (id: string) => void
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <>
      {toasts.map((toast, index) => (
        <div
          key={toast.id}
          style={{ top: `${80 + index * 80}px` }}
          className="fixed right-4 z-50"
        >
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => onRemove(toast.id)}
            action={toast.action}
          />
        </div>
      ))}
    </>
  )
}

