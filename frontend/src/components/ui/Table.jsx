import React from 'react';
import { EmptyState } from './UIPrimitives';

export const TableWrapper = ({ columns, rows, renderRow, className = '' }) => {
  return (
    <div className={`overflow-auto thin-scrollbar ${className}`}>
      <table className="w-full text-sm min-w-[900px]">
        <thead className="sticky top-0 bg-slate-900 z-10">
          <tr>
            {columns.map((col) => (
              <th key={col} className="text-left px-3 py-3 border-b border-border text-muted font-medium whitespace-nowrap">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length}>
                <EmptyState title="No rows found" subtitle="Try changing filters or search query." />
              </td>
            </tr>
          ) : (
            rows.map(renderRow)
          )}
        </tbody>
      </table>
    </div>
  );
};
