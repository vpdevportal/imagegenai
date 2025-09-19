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
        return 'bg-green-50 border-green-200'
      case 'error':
        return 'bg-red-50 border-red-200'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200'
      case 'info':
      default:
        return 'bg-blue-50 border-blue-200'
    }
  }

  const getTitleColor = () => {
    switch (toast.type) {
      case 'success':
        return 'text-green-800'
      case 'error':
        return 'text-red-800'
      case 'warning':
        return 'text-yellow-800'
      case 'info':
      default:
        return 'text-blue-800'
    }
  }

  const getMessageColor = () => {
    switch (toast.type) {
      case 'success':
        return 'text-green-700'
      case 'error':
        return 'text-red-700'
      case 'warning':
        return 'text-yellow-700'
      case 'info':
      default:
        return 'text-blue-700'
    }
  }

  return (
    <div className={`w-80 max-w-sm ${getBackgroundColor()} border rounded-lg shadow-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden`}>
      <div className="p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            {getIcon()}
          </div>
          <div className="ml-3 flex-1 pt-0.5 min-w-0">
            <p className={`text-sm font-medium ${getTitleColor()}`}>
              {toast.title}
            </p>
            {toast.message && (
              <p className={`mt-1 text-sm ${getMessageColor()}`}>
                {toast.message}
              </p>
            )}
          </div>
          <div className="ml-4 flex-shrink-0 flex">
            <button
              className={`rounded-md inline-flex ${getTitleColor()} hover:opacity-75 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
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
