'use client'

import React from 'react'
import { ExclamationTriangleIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface ConfirmationDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'danger' | 'warning' | 'info'
  isLoading?: boolean
}

export default function ConfirmationDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  type = 'danger',
  isLoading = false
}: ConfirmationDialogProps) {
  if (!isOpen) return null

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const getTypeStyles = () => {
    switch (type) {
      case 'danger':
        return {
          icon: 'text-red-400',
          confirmButton: 'bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 focus:ring-red-500',
          iconBg: 'bg-red-900/30'
        }
      case 'warning':
        return {
          icon: 'text-yellow-400',
          confirmButton: 'bg-gradient-to-r from-yellow-600 to-amber-600 hover:from-yellow-700 hover:to-amber-700 focus:ring-yellow-500',
          iconBg: 'bg-yellow-900/30'
        }
      case 'info':
        return {
          icon: 'text-blue-400',
          confirmButton: 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:ring-blue-500',
          iconBg: 'bg-blue-900/30'
        }
      default:
        return {
          icon: 'text-red-400',
          confirmButton: 'bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 focus:ring-red-500',
          iconBg: 'bg-red-900/30'
        }
    }
  }

  const styles = getTypeStyles()

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity"
          onClick={handleBackdropClick}
        />
        
        {/* Dialog */}
        <div className="relative transform overflow-hidden rounded-2xl bg-gray-800/95 backdrop-blur-xl text-left shadow-2xl border border-gray-700/50 transition-all sm:my-8 sm:w-full sm:max-w-lg">
          <div className="px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
            <div className="sm:flex sm:items-start">
              {/* Icon */}
              <div className={`mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full ${styles.iconBg} border-2 border-gray-700/50 sm:mx-0 sm:h-10 sm:w-10`}>
                <ExclamationTriangleIcon className={`h-6 w-6 ${styles.icon}`} aria-hidden="true" />
              </div>
              
              {/* Content */}
              <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                <h3 className="text-base font-semibold leading-6 text-gray-200">
                  {title}
                </h3>
                <div className="mt-2">
                  <p className="text-sm text-gray-400">
                    {message}
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Actions */}
          <div className="bg-gray-800/50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 border-t border-gray-700/50">
            <button
              type="button"
              className={`inline-flex w-full justify-center rounded-xl px-4 py-2.5 text-sm font-semibold text-white shadow-lg sm:ml-3 sm:w-auto ${styles.confirmButton} disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 active:scale-95`}
              onClick={onConfirm}
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                  Deleting...
                </div>
              ) : (
                confirmText
              )}
            </button>
            <button
              type="button"
              className="mt-3 inline-flex w-full justify-center rounded-xl bg-gray-700/50 hover:bg-gray-700 px-4 py-2.5 text-sm font-semibold text-gray-200 shadow-lg border border-gray-600/50 sm:mt-0 sm:w-auto transition-all duration-300 transform hover:scale-105 active:scale-95"
              onClick={onClose}
              disabled={isLoading}
            >
              {cancelText}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
