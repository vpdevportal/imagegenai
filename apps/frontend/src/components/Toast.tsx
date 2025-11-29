'use client'

import React from 'react'
import { useToast, Toast as ToastType } from '@/contexts/ToastContext'
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  InformationCircleIcon, 
  XCircleIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline'

const Toast: React.FC<{ toast: ToastType }> = ({ toast }) => {
  const { removeToast } = useToast()

  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-400" />
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-400" />
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
      case 'info':
      default:
        return <InformationCircleIcon className="h-5 w-5 text-blue-400" />
    }
  }

  const getBackgroundColor = () => {
    switch (toast.type) {
      case 'success':
        return 'bg-green-900/30 border-green-700/50'
      case 'error':
        return 'bg-red-900/30 border-red-700/50'
      case 'warning':
        return 'bg-yellow-900/30 border-yellow-700/50'
      case 'info':
      default:
        return 'bg-blue-900/30 border-blue-700/50'
    }
  }

  const getTitleColor = () => {
    switch (toast.type) {
      case 'success':
        return 'text-green-300'
      case 'error':
        return 'text-red-300'
      case 'warning':
        return 'text-yellow-300'
      case 'info':
      default:
        return 'text-blue-300'
    }
  }

  const getMessageColor = () => {
    switch (toast.type) {
      case 'success':
        return 'text-green-400'
      case 'error':
        return 'text-red-400'
      case 'warning':
        return 'text-yellow-400'
      case 'info':
      default:
        return 'text-blue-400'
    }
  }

  return (
    <div className={`w-80 max-w-sm ${getBackgroundColor()} border-2 rounded-2xl shadow-2xl pointer-events-auto backdrop-blur-sm overflow-hidden transform transition-all duration-300 hover:scale-[1.02]`}>
      <div className="p-5">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <div className="p-2 rounded-xl bg-gray-800/50 backdrop-blur-sm">
              {getIcon()}
            </div>
          </div>
          <div className="ml-3 flex-1 pt-0.5 min-w-0">
            <p className={`text-sm font-semibold ${getTitleColor()}`}>
              {toast.title}
            </p>
            {toast.message && (
              <p className={`mt-1.5 text-sm ${getMessageColor()}`}>
                {toast.message}
              </p>
            )}
          </div>
          <div className="ml-4 flex-shrink-0 flex">
            <button
              className={`rounded-xl inline-flex p-1.5 ${getTitleColor()} hover:bg-gray-800/50 backdrop-blur-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transform hover:scale-110 active:scale-95`}
              onClick={() => removeToast(toast.id)}
            >
              <span className="sr-only">Close</span>
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export const ToastContainer: React.FC = () => {
  const { toasts } = useToast()

  if (toasts.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm w-full">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} />
      ))}
    </div>
  )
}
